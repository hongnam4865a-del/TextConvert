#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""转换引擎基类"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Set


class BaseEngine(ABC):
    """所有转换引擎的抽象基类"""

    name: str = "base"

    @property
    @abstractmethod
    def supported_sources(self) -> Set[str]:
        """引擎能读取的源格式集合"""
        raise NotImplementedError

    @property
    @abstractmethod
    def supported_targets(self) -> Set[str]:
        """引擎能输出的目标格式集合"""
        raise NotImplementedError

    def can_handle(self, source_fmt: str, target_fmt: str) -> bool:
        """是否能直接处理 source -> target"""
        return source_fmt.lower() in self.supported_sources and target_fmt.lower() in self.supported_targets

    @abstractmethod
    def to_html(self, src_path: Path, dest_path: Path) -> Path:
        """将源文件转换为 HTML"""
        raise NotImplementedError

    @abstractmethod
    def from_html(self, html_path: Path, dest_path: Path) -> Path:
        """将 HTML 转换为目标格式"""
        raise NotImplementedError

    def is_available(self) -> bool:
        """引擎在当前环境是否可用（用于外部命令检查）"""
        return True
