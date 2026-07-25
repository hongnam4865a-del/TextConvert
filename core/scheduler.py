#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一转换调度核心"""

import shutil
import tempfile
import uuid
from pathlib import Path
from typing import List, Optional, Union

from config import DEFAULT_WORK_DIR, OUTPUT_DIR_NAME, TEMP_DIR_NAME
from core.format_detector import detect_format
from core.router import get_engine_for_step, plan_conversion
from utils.file_utils import clean_temp_dir, copy_to_output, ensure_dir
from utils.logger import get_logger, setup_logging


logger = get_logger("textconvert")


class ConversionError(Exception):
    """转换异常"""
    pass


def _prepare_work_dirs(work_dir: Path):
    """创建输出、临时、日志目录"""
    ensure_dir(work_dir / OUTPUT_DIR_NAME)
    ensure_dir(work_dir / TEMP_DIR_NAME)


def _generate_temp_path(work_dir: Path, suffix: str) -> Path:
    """生成临时文件路径"""
    temp_dir = ensure_dir(work_dir / TEMP_DIR_NAME)
    return temp_dir / f"{uuid.uuid4().hex}{suffix}"


def convert_file(
    input_path: Union[str, Path],
    target_format: str,
    output_path: Optional[Union[str, Path]] = None,
    work_dir: Optional[Union[str, Path]] = None,
    keep_temp: bool = False,
) -> Path:
    """统一转换入口

    Args:
        input_path: 源文件路径
        target_format: 目标格式（如 'html', 'txt', 'epub'）
        output_path: 自定义输出路径，None 则输出到工作区 output 目录
        work_dir: 工作区根目录，None 使用 DEFAULT_WORK_DIR
        keep_temp: 是否保留临时文件

    Returns:
        生成的目标文件路径

    Raises:
        ConversionError: 转换失败
    """
    input_path = Path(input_path).resolve()
    work_dir = Path(work_dir or DEFAULT_WORK_DIR).resolve()
    setup_logging(work_dir)
    _prepare_work_dirs(work_dir)

    try:
        source_fmt = detect_format(input_path)
    except ValueError as e:
        raise ConversionError(f"格式识别失败: {e}")

    target_fmt = target_format.lower().lstrip(".")
    logger.info(f"开始转换: {input_path} [{source_fmt}] -> [{target_fmt}]")

    if source_fmt == target_fmt:
        logger.warning("源格式与目标格式相同，执行复制")
        output = copy_to_output(input_path, work_dir / OUTPUT_DIR_NAME, f".{target_fmt}")
        return output

    steps = plan_conversion(source_fmt, target_fmt)
    if not steps:
        raise ConversionError(f"无法制定转换计划: {source_fmt} -> {target_fmt}")

    logger.debug(f"转换计划: {steps}")

    current_path = input_path
    temp_files: List[Path] = []

    try:
        for step_idx, (step_src, step_tgt) in enumerate(steps):
            engine = get_engine_for_step(step_src, step_tgt)
            is_last = step_idx == len(steps) - 1

            if is_last and output_path:
                dest_path = Path(output_path).resolve()
                ensure_dir(dest_path.parent)
            else:
                suffix = f".{step_tgt}"
                dest_path = _generate_temp_path(work_dir, suffix)

            logger.info(f"步骤 {step_idx + 1}/{len(steps)}: {step_src} -> {step_tgt} 使用 {engine.name}")

            try:
                if step_src == "html":
                    result = engine.from_html(current_path, dest_path)
                else:
                    result = engine.to_html(current_path, dest_path)
            except Exception as e:
                raise ConversionError(
                    f"{engine.name} 转换失败 ({step_src} -> {step_tgt}): {e}"
                ) from e

            if not result.exists():
                raise ConversionError(f"引擎未生成文件: {dest_path}")

            if not is_last:
                temp_files.append(dest_path)
            current_path = result

        # 最后一步结果如果不是用户指定的 output_path，复制到 output 目录
        if output_path is None:
            final_output = copy_to_output(
                current_path,
                work_dir / OUTPUT_DIR_NAME,
                f".{target_fmt}",
                name=input_path.stem,
            )
        else:
            final_output = current_path

        logger.info(f"转换完成: {final_output}")
        return final_output

    finally:
        if not keep_temp:
            for tf in temp_files:
                try:
                    if tf.exists():
                        tf.unlink()
                except Exception as e:
                    logger.warning(f"清理临时文件失败 {tf}: {e}")


def batch_convert(
    input_path: Union[str, Path],
    target_format: str,
    work_dir: Optional[Union[str, Path]] = None,
    recursive: bool = False,
) -> List[Path]:
    """批量转换

    Args:
        input_path: 文件或文件夹路径
        target_format: 目标格式
        work_dir: 工作区根目录
        recursive: 是否递归遍历子文件夹

    Returns:
        成功生成的文件路径列表
    """
    input_path = Path(input_path).resolve()
    work_dir = Path(work_dir or DEFAULT_WORK_DIR).resolve()
    setup_logging(work_dir)

    # 收集待转换文件
    if input_path.is_file():
        files = [input_path]
    elif input_path.is_dir():
        pattern = "**/*" if recursive else "*"
        files = [
            p for p in input_path.glob(pattern)
            if p.is_file() and not p.name.startswith("~$")
        ]
    else:
        logger.error(f"输入路径不存在: {input_path}")
        return []

    results: List[Path] = []
    for src in files:
        try:
            result = convert_file(src, target_format, work_dir=work_dir)
            results.append(result)
        except ConversionError as e:
            logger.error(f"跳过文件 {src}: {e}")
        except Exception as e:
            logger.exception(f"未捕获异常，跳过 {src}: {e}")

    logger.info(f"批量转换完成: 成功 {len(results)}/{len(files)}")
    return results
