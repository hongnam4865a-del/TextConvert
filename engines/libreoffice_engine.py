#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LibreOffice 外部引擎封装"""

import shutil
import subprocess
from pathlib import Path
from typing import Set

from config import ENGINE_TIMEOUT, LIBREOFFICE
from engines.base import BaseEngine
from utils.file_utils import ensure_dir


class LibreOfficeEngine(BaseEngine):
    """LibreOffice 办公文档转换引擎"""

    name = "libreoffice"

    _formats = {"docx", "html", "htm", "pdf", "odt", "rtf"}

    @property
    def supported_sources(self) -> Set[str]:
        return self._formats

    @property
    def supported_targets(self) -> Set[str]:
        return self._formats

    def is_available(self) -> bool:
        return shutil.which(LIBREOFFICE) is not None

    def _run(self, src_path: Path, dest_path: Path) -> Path:
        if not self.is_available():
            raise RuntimeError(
                f"LibreOffice 引擎不可用，请安装 LibreOffice 并确保 {LIBREOFFICE} 在 PATH 中"
            )
        ensure_dir(dest_path.parent)
        out_dir = dest_path.parent
        cmd = [
            LIBREOFFICE,
            "--headless",
            "--convert-to",
            dest_path.suffix.lstrip("."),
            "--outdir",
            str(out_dir),
            str(src_path),
        ]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=ENGINE_TIMEOUT,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"LibreOffice 转换失败: {result.stderr}")

        # LibreOffice 输出文件名与源文件相同，仅扩展名变化
        expected = out_dir / (src_path.stem + dest_path.suffix)
        if expected.exists() and expected != dest_path:
            shutil.move(str(expected), str(dest_path))
        if not dest_path.exists():
            raise RuntimeError("LibreOffice 未生成目标文件")
        return dest_path

    def to_html(self, src_path: Path, dest_path: Path) -> Path:
        return self._run(src_path, dest_path)

    def from_html(self, html_path: Path, dest_path: Path) -> Path:
        return self._run(html_path, dest_path)
