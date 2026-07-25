#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TXT 与 HTML 互转引擎"""

import html as html_module
from pathlib import Path
from typing import Set

from bs4 import BeautifulSoup

from engines.base import BaseEngine
from utils.file_utils import safe_read_text, safe_write_text


class TextEngine(BaseEngine):
    """纯文本转换引擎"""

    name = "text"

    @property
    def supported_sources(self) -> Set[str]:
        return {"txt", "html", "htm"}

    @property
    def supported_targets(self) -> Set[str]:
        return {"txt", "html", "htm"}

    def to_html(self, src_path: Path, dest_path: Path) -> Path:
        """TXT -> HTML：将段落包裹在 <p> 中"""
        text = safe_read_text(src_path)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        body = "\n".join(f"<p>{html_module.escape(p)}</p>" for p in paragraphs)

        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{html_module.escape(src_path.stem)}</title>
    <style>body {{ font-family: Georgia, serif; line-height: 1.7; max-width: 800px; margin: 40px auto; padding: 0 20px; }}</style>
</head>
<body>
{body}
</body>
</html>
"""
        safe_write_text(dest_path, html_doc)
        return dest_path

    def from_html(self, html_path: Path, dest_path: Path) -> Path:
        """HTML -> TXT：提取纯文本"""
        html = safe_read_text(html_path)
        soup = BeautifulSoup(html, "lxml")
        # 移除脚本和样式
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text("\n", strip=True)
        safe_write_text(dest_path, text)
        return dest_path
