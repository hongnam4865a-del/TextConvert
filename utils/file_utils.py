#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文件处理工具"""

import shutil
from pathlib import Path
from typing import Union


def ensure_dir(path: Path) -> Path:
    """确保目录存在，返回目录路径"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_read_text(path: Path, encoding: str = "utf-8", errors: str = "replace") -> str:
    """安全读取文本文件"""
    return path.read_text(encoding=encoding, errors=errors)


def safe_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    """安全写入文本文件，自动创建父目录"""
    ensure_dir(path.parent)
    path.write_text(content, encoding=encoding)


def copy_to_output(src: Path, output_dir: Path, suffix: str = None, name: str = None) -> Path:
    """复制文件到输出目录"""
    ensure_dir(output_dir)
    stem = name or src.stem
    ext = suffix or src.suffix
    dest = output_dir / f"{stem}{ext}"
    counter = 1
    while dest.exists():
        dest = output_dir / f"{stem}_{counter}{ext}"
        counter += 1
    shutil.copy2(src, dest)
    return dest


def clean_temp_dir(temp_dir: Path) -> None:
    """清理临时目录"""
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
