#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""命令行入口"""

import argparse
import sys
from pathlib import Path

from config import DEFAULT_WORK_DIR, SUPPORTED_FORMATS
from core.scheduler import batch_convert, convert_file


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="本地离线文本/电子书格式转换工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
支持格式: {', '.join(sorted(SUPPORTED_FORMATS))}
示例:
  python cli.py input.pdf -f html
  python cli.py input.md -f docx -o output.docx
  python cli.py ./books -f epub -r
""",
    )
    parser.add_argument("input", help="输入文件或目录路径")
    parser.add_argument(
        "-f", "--format", required=True, help="目标格式（如 html, txt, epub, pdf）"
    )
    parser.add_argument("-o", "--output", help="自定义输出文件路径")
    parser.add_argument(
        "-w", "--work-dir", default=str(DEFAULT_WORK_DIR), help=f"工作区目录（默认: {DEFAULT_WORK_DIR}）"
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="递归处理子目录（仅对目录有效）"
    )
    parser.add_argument(
        "--keep-temp", action="store_true", help="保留临时文件（调试用）"
    )

    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None

    try:
        if input_path.is_dir():
            results = batch_convert(
                input_path,
                args.format,
                work_dir=args.work_dir,
                recursive=args.recursive,
            )
            if results:
                print("\n转换成功的文件:")
                for r in results:
                    print(f"  {r}")
            else:
                print("没有文件转换成功。")
                sys.exit(1)
        else:
            result = convert_file(
                input_path,
                args.format,
                output_path=output_path,
                work_dir=args.work_dir,
                keep_temp=args.keep_temp,
            )
            print(f"\n转换完成: {result}")
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
