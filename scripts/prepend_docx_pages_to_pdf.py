#!/usr/bin/env python3
"""将 Word 前 N 页转为 PDF 后，拼接到现有 PDF 前面。

封面页按正文 PDF 首页的 MediaBox 做等比缩放并居中，避免 Word 导出为 Letter/A4
或与 LaTeX 版心不一致时拼版错位。
可选：在 Windows 上用 Word 将工作副本设为 A4 + 与 thesis 相同的页边距后再导出 PDF。
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
    """将文档设为 A4，页边距与 main_inner.tex 中 geometry 一致（左/右/下 2.5cm，上 22mm≈2.2cm）。"""
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
            ps.PaperSize = 9  # wdPaperA4
        except Exception:
            pass  # 部分模板锁定用纸型，仅改边距即可
        ps.TopMargin = app.CentimetersToPoints(2.2)  # 与 geometry top=22mm 一致
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


def add_cover_page_fitted(writer: PdfWriter, cover_page, target_w: float, target_h: float) -> None:
    """将封面页等比缩放后置于 target_w x target_h 空白页上居中（不拉伸变形）。"""
    cw, ch = _mediabox_size(cover_page)
    if cw <= 0 or ch <= 0:
        writer.add_page(cover_page)
        return
    scale = min(target_w / cw, target_h / ch)
    sw, sh = cw * scale, ch * scale
    tx = (target_w - sw) / 2
    ty = (target_h - sh) / 2
    blank = writer.add_blank_page(width=target_w, height=target_h)
    tr = Transformation().scale(scale, scale).translate(tx, ty)
    blank.merge_transformed_page(cover_page, tr)


def main() -> int:
    parser = argparse.ArgumentParser(description="DOCX 前 N 页 + PDF 合并（封面页对齐正文页面尺寸）")
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
        default=6,
        help="从 Word 转换结果中取前几页（默认 6，与「封面前六页」一致）",
    )
    parser.add_argument(
        "--no-fit-pages",
        action="store_true",
        help="禁用按正文页面框缩放封面（不推荐，仅调试）",
    )
    parser.add_argument(
        "--fix-word-margins",
        dest="fix_word_margins",
        action="store_true",
        default=False,
        help="转换前用 Word 将临时副本页边距对齐 thesis（需 Word + pywin32；模板锁定用纸型时可能失败）",
    )
    args = parser.parse_args()

    if not args.docx.is_file():
        print(f"找不到 DOCX: {args.docx}", file=sys.stderr)
        return 1
    if not args.main_pdf.is_file():
        print(f"找不到 PDF: {args.main_pdf}", file=sys.stderr)
        return 1

    out = args.output or (args.main_pdf.parent / "main_with_cover.pdf")
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
        n = max(0, args.pages)
        n = min(n, len(cover.pages))

        writer = PdfWriter()
        for i in range(n):
            if args.no_fit_pages:
                writer.add_page(cover.pages[i])
            else:
                add_cover_page_fitted(writer, cover.pages[i], target_w, target_h)
        for p in body.pages:
            writer.add_page(p)

        out.parent.mkdir(parents=True, exist_ok=True)
        tmp_out = out.parent / f".{out.stem}_tmp_{os.getpid()}.pdf"
        with open(tmp_out, "wb") as f:
            writer.write(f)
        try:
            os.replace(tmp_out, out)
        except OSError as exc:
            alt = out.with_name(f"{out.stem}_new{out.suffix}")
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
        f"已写入: {out.resolve()}（封面 {n} 页已对齐至 {target_w:.0f}x{target_h:.0f} pt + 正文 {len(body.pages)} 页，共 {len(writer.pages)} 页）"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
