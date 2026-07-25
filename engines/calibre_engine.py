#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Calibre ebook-convert 外部引擎封装"""

import shutil
import subprocess
from pathlib import Path
from typing import Set

from config import CALIBRE_CONVERT, ENGINE_TIMEOUT
from engines.base import BaseEngine
from utils.file_utils import ensure_dir


class CalibreEngine(BaseEngine):
    """Calibre 电子书转换引擎"""

    name = "calibre"

    # Calibre 支持的常见文本/电子书格式
    _formats = {"epub", "mobi", "azw3", "txt", "html", "htm", "pdf"}

    @property
    def supported_sources(self) -> Set[str]:
        return self._formats

    @property
    def supported_targets(self) -> Set[str]:
        return self._formats

    def is_available(self) -> bool:
        return shutil.which(CALIBRE_CONVERT) is not None

    def _run(self, src_path: Path, dest_path: Path) -> Path:
        if not self.is_available():
            raise RuntimeError(
                f"Calibre 引擎不可用，请安装 Calibre 并确保 {CALIBRE_CONVERT} 在 PATH 中"
            )
        ensure_dir(dest_path.parent)
        cmd = [CALIBRE_CONVERT, str(src_path), str(dest_path)]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=ENGINE_TIMEOUT,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Calibre 转换失败: {result.stderr}")
        if not dest_path.exists():
            raise RuntimeError("Calibre 未生成目标文件")
        return dest_path

    def to_html(self, src_path: Path, dest_path: Path) -> Path:
        return self._run(src_path, dest_path)

    def from_html(self, html_path: Path, dest_path: Path) -> Path:
        return self._run(html_path, dest_path)
