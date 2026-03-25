#!/usr/bin/env python3
"""将 Word 前 N 页转为 PDF 后，拼接到现有 PDF 前面。"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from docx2pdf import convert as docx_to_pdf
from pypdf import PdfReader, PdfWriter


def main() -> int:
    parser = argparse.ArgumentParser(description="DOCX 前 N 页 + PDF 合并")
    parser.add_argument("docx", type=Path, help="封面等 Word 文件")
    parser.add_argument("main_pdf", type=Path, help="正文 PDF，如 main.pdf")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="输出 PDF（默认：与 main 同目录的 main_with_cover.pdf）",
    )
    parser.add_argument(
        "-n",
        "--pages",
        type=int,
        default=4,
        help="从 Word 转换结果中取前几页（默认 4）",
    )
    args = parser.parse_args()

    if not args.docx.is_file():
        print(f"找不到 DOCX: {args.docx}", file=sys.stderr)
        return 1
    if not args.main_pdf.is_file():
        print(f"找不到 PDF: {args.main_pdf}", file=sys.stderr)
        return 1

    out = args.output or (args.main_pdf.parent / "main_with_cover.pdf")

    with tempfile.TemporaryDirectory() as td:
        tmp_pdf = Path(td) / "cover_full.pdf"
        # docx2pdf 需要输出为具体 .pdf 路径
        docx_to_pdf(str(args.docx.resolve()), str(tmp_pdf))
        if not tmp_pdf.is_file():
            print("Word 转 PDF 失败（未生成临时文件）。", file=sys.stderr)
            return 1

        cover = PdfReader(str(tmp_pdf))
        body = PdfReader(str(args.main_pdf))

        n = max(0, args.pages)
        n = min(n, len(cover.pages))

        writer = PdfWriter()
        for i in range(n):
            writer.add_page(cover.pages[i])
        for p in body.pages:
            writer.add_page(p)

        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "wb") as f:
            writer.write(f)

    print(f"已写入: {out.resolve()}（封面 {n} 页 + 正文 {len(body.pages)} 页，共 {len(writer.pages)} 页）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
