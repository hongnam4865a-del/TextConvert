#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全局配置"""

from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.resolve()

# 默认工作区（可在运行时覆盖）
DEFAULT_WORK_DIR = Path("D:/TextConvertWorkspace")

# 子目录
OUTPUT_DIR_NAME = "output"
TEMP_DIR_NAME = "temp"
LOG_DIR_NAME = "log"

# 支持的文本/电子书格式
SUPPORTED_FORMATS = {
    "txt", "md", "html", "htm", "docx", "epub", "mobi", "pdf",
}

# 外部引擎命令（Windows 示例路径，可在环境变量或配置中覆盖）
CALIBRE_CONVERT = "ebook-convert"
LIBREOFFICE = "soffice"

# 转换超时（秒）
ENGINE_TIMEOUT = 300

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
