#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WeasyPrint 引擎：HTML -> PDF（可选引擎）"""

from pathlib import Path
from typing import Set

from engines.base import BaseEngine
from utils.file_utils import ensure_dir


class WeasyPrintEngine(BaseEngine):
    """HTML 转 PDF 引擎。

    注意：WeasyPrint 在 Windows 上需要额外安装 GTK 运行时，
    因此采用懒加载，未安装时引擎自动标记为不可用。
    """

    name = "weasyprint"

    @property
    def supported_sources(self) -> Set[str]:
        return {"html", "htm"}

    @property
    def supported_targets(self) -> Set[str]:
        return {"pdf"}

    def is_available(self) -> bool:
        try:
            import weasyprint  # noqa: F401
            return True
        except Exception:
            return False

    def to_html(self, src_path: Path, dest_path: Path) -> Path:
        raise NotImplementedError("WeasyPrintEngine 仅支持 HTML -> PDF")

    def from_html(self, html_path: Path, dest_path: Path) -> Path:
        if not self.is_available():
            raise RuntimeError(
                "WeasyPrint 引擎不可用。Windows 用户需安装 GTK 运行时，"
                "详见 https://doc.courtbouillon.org/weasyprint/stable/first_steps.html"
            )
        from weasyprint import HTML
        ensure_dir(dest_path.parent)
        HTML(filename=str(html_path)).write_pdf(str(dest_path))
        return dest_path
