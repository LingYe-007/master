#!/usr/bin/env python3
"""将 Word 前 N 页转为 PDF 后，拼接到现有 PDF 前面。

封面页按正文 PDF 首页的 MediaBox 做等比缩放并居中，避免 Word 导出为 Letter/A4
或与 LaTeX 版心不一致时拼版错位。
可选：在 Windows 上用 Word 将工作副本设为 A4 + 与 thesis 相同的页边距后再导出 PDF。
"""
from __future__ import annotations

import argparse
import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

from docx2pdf import convert as docx_to_pdf_word
from pypdf import PdfReader, PdfWriter, Transformation


def _find_soffice() -> Optional[str]:
    for cmd in (
        "soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/local/bin/soffice",
    ):
        if shutil.which(cmd) or Path(cmd).is_file():
            return cmd
    return None


def docx_to_pdf(docx_path: Path, pdf_path: Path) -> bool:
    """优先 docx2pdf（需 Microsoft Word），失败则尝试 LibreOffice headless。"""
    try:
        docx_to_pdf_word(str(docx_path.resolve()), str(pdf_path))
        if pdf_path.is_file() and pdf_path.stat().st_size > 0:
            return True
    except Exception as exc:
        print(f"提示: docx2pdf 未成功（{exc}），尝试 LibreOffice…", file=sys.stderr)

    soffice = _find_soffice()
    if not soffice:
        return False

    outdir = pdf_path.parent
    outdir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            soffice,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(outdir),
            str(docx_path.resolve()),
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        if proc.stderr or proc.stdout:
            print(proc.stderr or proc.stdout, file=sys.stderr)
        return False

    generated = outdir / f"{docx_path.stem}.pdf"
    if not generated.is_file():
        return False
    if generated.resolve() != pdf_path.resolve():
        shutil.move(str(generated), str(pdf_path))
    return pdf_path.is_file() and pdf_path.stat().st_size > 0


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
    parser.add_argument(
        "docx",
        type=Path,
        nargs="?",
        default=None,
        help="封面 Word 文件（与 --cover-pdf 二选一）",
    )
    parser.add_argument("main_pdf", type=Path, help="正文 PDF，如 main.pdf")
    parser.add_argument(
        "--cover-pdf",
        type=Path,
        default=None,
        help="已导出的封面 PDF（跳过 DOCX 转换，可与 docx 二选一）",
    )
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
        help="从 Word 转换结果中取前几页（默认 6；若 Word 实际导出多于 n 页，其余页不会拼入，见 --use-all-cover-pages）",
    )
    parser.add_argument(
        "--use-all-cover-pages",
        action="store_true",
        help="使用 Word 导出 PDF 的全部页数（避免「文件名写前六页但实际多 1 页空白/声明」时丢页）",
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

    cover_pdf_arg = getattr(args, "cover_pdf", None)
    if cover_pdf_arg is None and (args.docx is None or not args.docx.is_file()):
        print("请提供封面 DOCX，或使用 --cover-pdf 指定已导出的封面 PDF。", file=sys.stderr)
        return 1
    if cover_pdf_arg is not None and not cover_pdf_arg.is_file():
        print(f"找不到封面 PDF: {cover_pdf_arg}", file=sys.stderr)
        return 1
    if not args.main_pdf.is_file():
        print(f"找不到 PDF: {args.main_pdf}", file=sys.stderr)
        return 1

    out = args.output or (args.main_pdf.parent / "main_with_cover.pdf")
    body = PdfReader(str(args.main_pdf))
    target_w, target_h = _mediabox_size(body.pages[0])

    tmp_holder = None
    cover_src: Path
    if cover_pdf_arg is not None:
        cover_src = cover_pdf_arg
        ctx = contextlib.nullcontext()
    else:
        tmp_holder = tempfile.TemporaryDirectory()
        td_path = Path(tmp_holder.name)
        tmp_pdf = td_path / "cover_full.pdf"
        work_docx = td_path / "cover_work.docx"
        shutil.copy(args.docx, work_docx)
        if getattr(args, "fix_word_margins", False):
            _apply_word_margins_a4(work_docx)
        if not docx_to_pdf(work_docx, tmp_pdf):
            print(
                "DOCX 转 PDF 失败：请安装 Microsoft Word 或 LibreOffice；"
                "或在 WPS 中打开封面 DOCX 导出 PDF 后执行：\n"
                f"  python3 scripts/prepend_docx_pages_to_pdf.py --cover-pdf 封面.pdf "
                f"{args.main_pdf} -o ... -n 6",
                file=sys.stderr,
            )
            return 1
        cover_src = tmp_pdf
        ctx = tmp_holder

    with ctx:
        cover = PdfReader(str(cover_src))
        total_cover = len(cover.pages)
        if getattr(args, "use_all_cover_pages", False):
            n = total_cover
        else:
            n = max(0, args.pages)
            n = min(n, total_cover)
        if total_cover > n:
            print(
                f"警告: Word 导出共 {total_cover} 页，本次仅拼接前 {n} 页（未写入后 {total_cover - n} 页）。"
                f"如需全部拼接请使用 --use-all-cover-pages 或 -n {total_cover}。",
                file=sys.stderr,
            )
        elif not getattr(args, "use_all_cover_pages", False) and args.pages > total_cover:
            print(
                f"提示: Word 导出仅 {total_cover} 页（少于 -n {args.pages}），已全部拼接。",
                file=sys.stderr,
            )

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
