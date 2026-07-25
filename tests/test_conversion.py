#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""集成测试脚本：验证核心转换路径"""

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.format_detector import detect_format
from core.scheduler import batch_convert, convert_file

WORK_DIR = Path("D:/TextConvertWorkspace_test")
TEST_INPUTS = Path("D:/TextConvertWorkspace_test/inputs")


def setup():
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    TEST_INPUTS.mkdir(parents=True, exist_ok=True)

    # 创建测试文件
    (TEST_INPUTS / "hello.txt").write_text(
        "Hello World\n\nThis is a test text file.", encoding="utf-8"
    )
    (TEST_INPUTS / "note.md").write_text(
        "# Note\n\nThis is **markdown**.", encoding="utf-8"
    )


def test_detection():
    assert detect_format(TEST_INPUTS / "hello.txt") == "txt"
    assert detect_format(TEST_INPUTS / "note.md") == "md"
    print("[OK] format detection")


def test_txt_to_html():
    result = convert_file(TEST_INPUTS / "hello.txt", "html", work_dir=WORK_DIR)
    assert result.exists() and result.suffix == ".html"
    print(f"[OK] txt -> html: {result}")


def test_md_to_txt():
    result = convert_file(TEST_INPUTS / "note.md", "txt", work_dir=WORK_DIR)
    assert result.exists() and result.suffix == ".txt"
    print(f"[OK] md -> txt: {result}")


def test_md_to_docx():
    result = convert_file(TEST_INPUTS / "note.md", "docx", work_dir=WORK_DIR)
    assert result.exists() and result.suffix == ".docx"
    print(f"[OK] md -> docx: {result}")


def test_batch():
    results = batch_convert(TEST_INPUTS, "html", work_dir=WORK_DIR)
    assert len(results) == 2
    print(f"[OK] batch convert: {len(results)} files")


def main():
    setup()
    test_detection()
    test_txt_to_html()
    test_md_to_txt()
    test_md_to_docx()
    test_batch()
    print("\nAll tests passed.")


if __name__ == "__main__":
    main()
