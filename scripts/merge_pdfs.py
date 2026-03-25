#!/usr/bin/env python3
"""按顺序拼接多个 PDF 为一个文件。依赖: pip install pypdf

用法:
  python scripts/merge_pdfs.py 输出.pdf 第一个.pdf 第二个.pdf [第三个.pdf ...]

示例:
  python scripts/merge_pdfs.py main_full.pdf main.pdf 封面授权.pdf
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def main() -> int:
    parser = argparse.ArgumentParser(description="按顺序合并多个 PDF")
    parser.add_argument(
        "output",
        type=Path,
        help="合并后的输出 PDF 路径",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help="按先后顺序参与合并的源 PDF（至少一个）",
    )
    args = parser.parse_args()

    writer = PdfWriter()
    for path in args.inputs:
        if not path.is_file():
            print(f"错误: 找不到文件: {path}", file=sys.stderr)
            return 1
        reader = PdfReader(str(path))
        if getattr(reader, "is_encrypted", False) and reader.decrypt("") == 0:
            print(f"错误: 文件已加密，无法合并: {path}", file=sys.stderr)
            return 1
        for page in reader.pages:
            writer.add_page(page)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "wb") as f:
        writer.write(f)
    print(f"已写入: {args.output.resolve()} （共 {len(writer.pages)} 页）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
