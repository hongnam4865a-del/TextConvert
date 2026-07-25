#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""日志模块"""

import logging
import sys
from datetime import datetime
from pathlib import Path

from config import LOG_DIR_NAME, LOG_FORMAT, LOG_LEVEL


def get_logger(name: str = "textconvert") -> logging.Logger:
    """获取统一日志记录器"""
    return logging.getLogger(name)


def setup_logging(work_dir: Path, level: str = LOG_LEVEL) -> logging.Logger:
    """配置日志：同时输出到控制台和文件"""
    logger = logging.getLogger("textconvert")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT)

    # 控制台输出
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # 文件输出
    log_dir = work_dir / LOG_DIR_NAME
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"convert_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
