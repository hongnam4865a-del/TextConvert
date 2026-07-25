#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown 与 HTML 互转引擎"""

from pathlib import Path
from typing import Set

import markdown
from bs4 import BeautifulSoup

from engines.base import BaseEngine
from utils.file_utils import safe_read_text, safe_write_text


class MarkdownEngine(BaseEngine):
    """Markdown 转换引擎"""

    name = "markdown"

    @property
    def supported_sources(self) -> Set[str]:
        return {"md", "html", "htm"}

    @property
    def supported_targets(self) -> Set[str]:
        return {"md", "html", "htm"}

    def to_html(self, src_path: Path, dest_path: Path) -> Path:
        """MD -> HTML"""
        md_text = safe_read_text(src_path)
        html_body = markdown.markdown(
            md_text,
            extensions=["extra", "toc", "tables", "fenced_code"],
        )
        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{src_path.stem}</title>
    <style>body {{ font-family: Georgia, serif; line-height: 1.7; max-width: 800px; margin: 40px auto; padding: 0 20px; }}</style>
</head>
<body>
{html_body}
</body>
</html>
"""
        safe_write_text(dest_path, html_doc)
        return dest_path

    def from_html(self, html_path: Path, dest_path: Path) -> Path:
        """HTML -> MD：使用 BeautifulSoup 做简单反向转换"""
        html = safe_read_text(html_path)
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style"]):
            tag.decompose()

        md_lines = []
        for elem in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre", "blockquote"]):
            text = elem.get_text(strip=True)
            if not text:
                continue
            if elem.name == "h1":
                md_lines.append(f"# {text}")
            elif elem.name == "h2":
                md_lines.append(f"## {text}")
            elif elem.name == "h3":
                md_lines.append(f"### {text}")
            elif elem.name == "blockquote":
                md_lines.append(f"> {text}")
            elif elem.name == "li":
                md_lines.append(f"- {text}")
            elif elem.name == "pre":
                md_lines.append(f"```\n{text}\n```")
            else:
                md_lines.append(text)
            md_lines.append("")

        safe_write_text(dest_path, "\n".join(md_lines).strip())
        return dest_path
