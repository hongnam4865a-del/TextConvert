#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PyMuPDF 引擎：负责 PDF -> HTML 的高质量提取"""

import html as html_module
import re
from collections import Counter
from pathlib import Path
from typing import Set

import fitz

from engines.base import BaseEngine
from utils.file_utils import safe_write_text


# 软连字符与零宽字符
_CONTROL_CHARS = ("\u00ad", "\u200b", "\u200c", "\u200d", "\ufeff")


def _clean_text(text: str) -> str:
    for ch in _CONTROL_CHARS:
        text = text.replace(ch, "")
    return " ".join(text.split())


def _fix_line_break_hyphen(m: re.Match) -> str:
    left, right = m.group(1), m.group(2)
    keep_separate = {
        "a", "an", "and", "as", "at", "be", "by", "do", "for", "from",
        "in", "is", "it", "of", "on", "or", "so", "the", "to", "up",
    }
    if right.lower() in keep_separate:
        return f"{left} {right}"
    return f"{left}{right}"


class PyMuPDFEngine(BaseEngine):
    """PDF 转 HTML 引擎（基于 PyMuPDF）"""

    name = "pymupdf"

    @property
    def supported_sources(self) -> Set[str]:
        return {"pdf"}

    @property
    def supported_targets(self) -> Set[str]:
        return {"html", "htm"}

    def to_html(self, src_path: Path, dest_path: Path) -> Path:
        """PDF -> 语义化 HTML"""
        doc = fitz.open(src_path)
        page_bodies = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_html = self._extract_page_html(page, page_num + 1)
            page_bodies.append(
                f'<section class="page" data-page="{page_num + 1}" aria-label="Page {page_num + 1}">\n'
                f"{text_html}\n"
                f"</section>\n"
            )

        doc.close()

        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_module.escape(src_path.stem)}</title>
    <style>
        body {{ font-family: Georgia, "Times New Roman", serif; font-size: 16px; line-height: 1.7; color: #222; margin: 0; padding: 20px; background: #f5f5f5; }}
        main {{ max-width: 800px; margin: 0 auto; }}
        .page {{ background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.15); margin-bottom: 24px; padding: 40px; box-sizing: border-box; }}
        h1, h2 {{ line-height: 1.3; margin-top: 1.2em; margin-bottom: 0.6em; }}
        h1 {{ font-size: 1.8em; }} h2 {{ font-size: 1.5em; }}
        p {{ margin: 0 0 1em 0; text-align: justify; }}
    </style>
</head>
<body>
<main>
{''.join(page_bodies)}
</main>
</body>
</html>
"""
        safe_write_text(dest_path, html_doc)
        return dest_path

    def from_html(self, html_path: Path, dest_path: Path) -> Path:
        """本引擎不负责 HTML -> PDF，请使用 WeasyPrintEngine"""
        raise NotImplementedError("PyMuPDFEngine 不支持 HTML -> PDF，请使用 WeasyPrint 引擎")

    def _extract_page_html(self, page: fitz.Page, page_num: int) -> str:
        """提取单页文本为语义化 HTML"""
        page_height = page.rect.height
        header_zone = 60
        footer_zone = page_height - 60

        text_blocks = page.get_text("blocks")
        dict_blocks = page.get_text("dict").get("blocks", [])

        font_info = {}
        for idx, block in enumerate(dict_blocks):
            if block.get("type") != 0:
                continue
            sizes, bolds = [], []
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if not span.get("text", "").strip():
                        continue
                    sizes.append(span.get("size", 0))
                    bolds.append(bool(span.get("flags", 0) & 16))
            if sizes:
                font_info[idx] = {
                    "size": sum(sizes) / len(sizes),
                    "bold": any(bolds),
                }

        elements = []
        for block_no, block in enumerate(text_blocks):
            x0, y0, x1, y1, text, bno, btype = block
            if btype != 0:
                continue
            text = _clean_text(text)
            text = re.sub(r"(\w+)-\s+(\w+)", _fix_line_break_hyphen, text)
            if not text:
                continue
            info = font_info.get(block_no, {})
            elements.append({
                "text": text,
                "size": info.get("size", 10),
                "bold": info.get("bold", False),
                "y": y0,
                "in_hf": y0 < header_zone or y0 > footer_zone,
            })

        if not elements:
            return ""

        rounded_sizes = [round(e["size"] * 2) / 2 for e in elements]
        body_size = Counter(rounded_sizes).most_common(1)[0][0]

        parts = []
        for idx, e in enumerate(elements):
            txt = html_module.escape(e["text"])
            looks_heading = (
                len(e["text"]) < 50
                and not e["text"].endswith((".", ":", "?", "!"))
                and not e["text"].isupper()
                and not e["in_hf"]
                and idx > 0
            )
            if e["size"] > body_size * 1.5:
                tag = "h1"
            elif (e["size"] > body_size * 1.2 and e["bold"]) or looks_heading:
                tag = "h2"
            else:
                tag = "p"
            parts.append(f"<{tag}>{txt}</{tag}>")

        return "\n".join(parts)
