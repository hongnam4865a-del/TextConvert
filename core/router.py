#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""转换路由分发模块

统一策略：源格式 -> HTML（通用中间层） -> 目标格式
外部引擎（Calibre / LibreOffice）若支持直接转换则优先使用。
"""

from typing import List, Tuple

from engines.calibre_engine import CalibreEngine
from engines.docx_engine import DocxEngine
from engines.epub_engine import EpubEngine
from engines.libreoffice_engine import LibreOfficeEngine
from engines.markdown_engine import MarkdownEngine
from engines.pymupdf_engine import PyMuPDFEngine
from engines.text_engine import TextEngine
from engines.weasyprint_engine import WeasyPrintEngine


_REGISTERED_ENGINES = [
    TextEngine(),
    MarkdownEngine(),
    PyMuPDFEngine(),
    DocxEngine(),
    EpubEngine(),
    WeasyPrintEngine(),
    CalibreEngine(),
    LibreOfficeEngine(),
]

_EXTERNAL_ENGINES = (CalibreEngine, LibreOfficeEngine)


def _normalize(fmt: str) -> str:
    return fmt.lower().lstrip(".")


def _find_direct_engine(source_fmt: str, target_fmt: str):
    """找到可用的外部直接转换引擎"""
    src = _normalize(source_fmt)
    tgt = _normalize(target_fmt)
    for engine in _REGISTERED_ENGINES:
        if isinstance(engine, _EXTERNAL_ENGINES):
            if engine.can_handle(src, tgt) and engine.is_available():
                return engine
    return None


def plan_conversion(source_fmt: str, target_fmt: str) -> List[Tuple[str, str]]:
    """制定转换计划，返回步骤列表 [(source, target), ...]"""
    src = _normalize(source_fmt)
    tgt = _normalize(target_fmt)

    if src == tgt:
        return []

    # 优先使用外部引擎直接转换（质量更高）
    if _find_direct_engine(src, tgt):
        return [(src, tgt)]

    # 否则走 HTML 中间层
    steps = []
    if src != "html":
        steps.append((src, "html"))
    if tgt != "html":
        steps.append(("html", tgt))
    return steps


def get_engine_for_step(source_fmt: str, target_fmt: str):
    """为单步转换获取可用引擎"""
    src = _normalize(source_fmt)
    tgt = _normalize(target_fmt)

    for engine in _REGISTERED_ENGINES:
        if engine.can_handle(src, tgt) and engine.is_available():
            return engine

    raise RuntimeError(
        f"找不到可用的转换引擎: {source_fmt} -> {target_fmt}"
    )
