#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文件格式识别模块

不依赖后缀名，优先读取文件头魔数识别真实类型，
后缀名仅作为 fallback。
"""

import struct
import zipfile
from pathlib import Path
from typing import Optional

from config import SUPPORTED_FORMATS


# 魔数映射
MAGIC_SIGNATURES = [
    (b"%PDF", "pdf"),
    (b"PK", "zip"),  # docx/epub 都是 zip 格式，需要进一步识别
    (b"\x9e\x0a\xa6\x00", "mobi"),  # MOBI/PRC
    (b"\x42\x4f\x4f\x4b\x4d\x4f\x42\x49", "mobi"),  # BOOKMOBI
    (b"<?xml", "xml"),
    (b"<!DOCTYPE", "html"),
    (b"<html", "html"),
]


def _read_head(path: Path, size: int = 64) -> bytes:
    """读取文件头部字节"""
    try:
        with open(path, "rb") as f:
            return f.read(size)
    except Exception:
        return b""


def _is_docx(data: bytes, path: Path) -> bool:
    """判断 ZIP 包是否为 DOCX"""
    if not zipfile.is_zipfile(path):
        return False
    try:
        with zipfile.ZipFile(path, "r") as z:
            return "word/document.xml" in z.namelist()
    except Exception:
        return False


def _is_epub(data: bytes, path: Path) -> bool:
    """判断 ZIP 包是否为 EPUB"""
    if not zipfile.is_zipfile(path):
        return False
    try:
        with zipfile.ZipFile(path, "r") as z:
            names = z.namelist()
            return "mimetype" in names or any(
                name.endswith(".opf") or name.endswith(".ncx") for name in names
            )
    except Exception:
        return False


def _guess_text_format(data: bytes, path: Path) -> Optional[str]:
    """对文本类文件做进一步识别"""
    try:
        text = data.decode("utf-8", errors="ignore")
    except Exception:
        return None

    lowered = text.lower().lstrip()
    if lowered.startswith(("<!doctype html", "<html", "<?xml")):
        return "html"

    # Markdown 特征：文件头出现常见 markdown 语法
    md_markers = ["# ", "## ", "```", "**", "[", "- ", "* ", "> "]
    first_lines = "\n".join(text.splitlines()[:20])
    if any(marker in first_lines for marker in md_markers) and path.suffix.lower() in (".md", ".markdown"):
        return "md"

    return "txt"


def detect_format(path: Path) -> str:
    """识别文件格式，返回小写扩展名字符串

    Raises:
        ValueError: 文件不存在或格式不支持
    """
    if not path.exists():
        raise ValueError(f"文件不存在: {path}")
    if path.is_dir():
        raise ValueError(f"路径是目录，不是文件: {path}")

    data = _read_head(path)
    fmt: Optional[str] = None

    # 1. 魔数识别
    for magic, candidate in MAGIC_SIGNATURES:
        if data.startswith(magic):
            fmt = candidate
            break

    # 2. ZIP 格式进一步区分 docx / epub
    if fmt == "zip":
        if _is_epub(data, path):
            fmt = "epub"
        elif _is_docx(data, path):
            fmt = "docx"
        else:
            fmt = None

    # 3. 文本类 fallback
    if fmt is None:
        fmt = _guess_text_format(data, path)

    # 4. 后缀名 fallback
    if fmt is None or fmt not in SUPPORTED_FORMATS:
        ext = path.suffix.lstrip(".").lower()
        if ext in SUPPORTED_FORMATS:
            fmt = ext

    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"不支持的文件格式: {path} (detected={fmt})")

    return fmt


def is_supported_format(fmt: str) -> bool:
    """判断格式是否在支持列表中"""
    return fmt.lower() in SUPPORTED_FORMATS
