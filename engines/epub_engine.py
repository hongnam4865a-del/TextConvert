#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EPUB 与 HTML 互转引擎（基于 ebooklib）"""

import html as html_module
from pathlib import Path
from typing import Set

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub

from engines.base import BaseEngine
from utils.file_utils import safe_read_text, safe_write_text


class EpubEngine(BaseEngine):
    """EPUB 转换引擎"""

    name = "epub"

    @property
    def supported_sources(self) -> Set[str]:
        return {"epub", "html", "htm"}

    @property
    def supported_targets(self) -> Set[str]:
        return {"epub", "html", "htm"}

    def to_html(self, src_path: Path, dest_path: Path) -> Path:
        """EPUB -> HTML：合并所有章节为一个 HTML"""
        book = epub.read_epub(str(src_path))
        parts = []
        title = src_path.stem

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), features="xml")
                # 提取 body 内容
                body = soup.find("body")
                if body:
                    parts.append(str(body.decode_contents()))
                else:
                    parts.append(str(soup))

        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{html_module.escape(title)}</title>
    <style>body {{ font-family: Georgia, serif; line-height: 1.7; max-width: 800px; margin: 40px auto; padding: 0 20px; }}</style>
</head>
<body>
<h1>{html_module.escape(title)}</h1>
{''.join(parts)}
</body>
</html>
"""
        safe_write_text(dest_path, html_doc)
        return dest_path

    def from_html(self, html_path: Path, dest_path: Path) -> Path:
        """HTML -> EPUB"""
        html = safe_read_text(html_path)
        soup = BeautifulSoup(html, "lxml")
        title = soup.find("title")
        title_text = title.get_text(strip=True) if title else html_path.stem

        book = epub.EpubBook()
        book.set_identifier(f"id_{html_path.stem}")
        book.set_title(title_text)
        book.set_language("en")
        book.add_author("TextConvert")

        chapter = epub.EpubHtml(title=title_text, file_name="chapter.xhtml", lang="en")
        chapter.content = html
        book.add_item(chapter)
        book.toc = (epub.Link("chapter.xhtml", title_text, "chapter"),)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = ["nav", chapter]
        epub.write_epub(str(dest_path), book)
        return dest_path
