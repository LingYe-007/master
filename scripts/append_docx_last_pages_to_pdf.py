#!/usr/bin/env python3
"""将 Word 文档最后 N 页转为 PDF 后，拼接到现有 PDF 末尾。

页面按正文 PDF 首页的 MediaBox 做等比缩放并居中（与 prepend_docx_pages_to_pdf 一致）。
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

from docx2pdf import convert as docx_to_pdf
from pypdf import PdfReader, PdfWriter, Transformation


def _mediabox_size(page) -> tuple[float, float]:
    mb = page.mediabox
    return float(mb.width), float(mb.height)


def _apply_word_margins_a4(docx_path: Path) -> None:
    try:
        import win32com.client  # type: ignore
    except ImportError:
        print("提示: 未安装 pywin32，跳过 Word 页边距统一（仍可依赖 PDF 缩放对齐页面尺寸）。", file=sys.stderr)
        return

    word = None
    doc = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(str(docx_path.resolve()), False, False, False)
        ps = doc.PageSetup
        app = doc.Application
        try:
            ps.PaperSize = 9
        except Exception:
            pass
        ps.TopMargin = app.CentimetersToPoints(2.2)
        ps.BottomMargin = app.CentimetersToPoints(2.5)
        ps.LeftMargin = app.CentimetersToPoints(2.5)
        ps.RightMargin = app.CentimetersToPoints(2.5)
        doc.Save()
    except Exception as exc:
        print(f"警告: Word 页边距统一失败（将仅用 PDF 缩放对齐页面框）: {exc}", file=sys.stderr)
    finally:
        if doc is not None:
            doc.Close(False)
        if word is not None:
            word.Quit()


def add_page_fitted(writer: PdfWriter, src_page, target_w: float, target_h: float) -> None:
    cw, ch = _mediabox_size(src_page)
    if cw <= 0 or ch <= 0:
        writer.add_page(src_page)
        return
    scale = min(target_w / cw, target_h / ch)
    sw, sh = cw * scale, ch * scale
    tx = (target_w - sw) / 2
    ty = (target_h - sh) / 2
    blank = writer.add_blank_page(width=target_w, height=target_h)
    tr = Transformation().scale(scale, scale).translate(tx, ty)
    blank.merge_transformed_page(src_page, tr)


def main() -> int:
    parser = argparse.ArgumentParser(description="DOCX 最后 N 页接到 PDF 末尾（按正文首页尺寸对齐）")
    parser.add_argument("docx", type=Path, help="封面等 Word 文件（如 封面.docx）")
    converter = parser.add_argument_group("合并目标")
    converter.add_argument(
        "main_pdf",
        type=Path,
        help="原有 PDF（如已含前封面的 main_with_cover.pdf）",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="输出 PDF（默认：覆盖与 main_pdf 相同路径）",
    )
    parser.add_argument(
        "-n",
        "--pages",
        type=int,
        default=2,
        help="从 Word 转换结果中取最后几页（默认 2）",
    )
    parser.add_argument(
        "--no-fit-pages",
        action="store_true",
        help="禁用按正文页面框缩放（不推荐，仅调试）",
    )
    parser.add_argument(
        "--fix-word-margins",
        dest="fix_word_margins",
        action="store_true",
        default=False,
        help="转换前用 Word 将临时副本页边距对齐 thesis（需 Word + pywin32）",
    )
    args = parser.parse_args()

    if not args.docx.is_file():
        print(f"找不到 DOCX: {args.docx}", file=sys.stderr)
        return 1
    if not args.main_pdf.is_file():
        print(f"找不到 PDF: {args.main_pdf}", file=sys.stderr)
        return 1
    if args.pages < 1:
        print("--pages 至少为 1", file=sys.stderr)
        return 1

    out = args.output or args.main_pdf
    body = PdfReader(str(args.main_pdf))
    target_w, target_h = _mediabox_size(body.pages[0])

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        tmp_pdf = td_path / "cover_full.pdf"
        work_docx = td_path / "cover_work.docx"
        shutil.copy(args.docx, work_docx)
        if getattr(args, "fix_word_margins", False):
            _apply_word_margins_a4(work_docx)
        docx_to_pdf(str(work_docx.resolve()), str(tmp_pdf))
        if not tmp_pdf.is_file():
            print("Word 转 PDF 失败（未生成临时文件）。", file=sys.stderr)
            return 1

        cover = PdfReader(str(tmp_pdf))
        total = len(cover.pages)
        n = min(args.pages, total)
        start = total - n

        writer = PdfWriter()
        for p in body.pages:
            writer.add_page(p)
        for i in range(start, total):
            if args.no_fit_pages:
                writer.add_page(cover.pages[i])
            else:
                add_page_fitted(writer, cover.pages[i], target_w, target_h)

        out.parent.mkdir(parents=True, exist_ok=True)
        tmp_out = out.parent / f".{out.stem}_append_tmp_{os.getpid()}.pdf"
        with open(tmp_out, "wb") as f:
            writer.write(f)
        try:
            os.replace(tmp_out, out)
        except OSError as exc:
            alt = out.with_name(f"{out.stem}_appended{out.suffix}")
            try:
                os.replace(tmp_out, alt)
            except OSError:
                tmp_out.unlink(missing_ok=True)
                raise exc
            print(
                f"警告: 无法覆盖 {out.name}（文件是否被打开？）。已改为写入: {alt.name}",
                file=sys.stderr,
            )
            out = alt

    print(
        f"已写入: {out.resolve()}（正文 {len(body.pages)} 页 + 文末 Word 最后 {n} 页，共 {len(writer.pages)} 页）"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
