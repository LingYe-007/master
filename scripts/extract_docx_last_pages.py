#!/usr/bin/env python3
"""
从完整 Word 文档中仅保留最后 N 页（删去该页起点之前的全部内容），版式、节属性尽量随内容保留。
做法与 extract_docx_first_pages.py 对称：先复制 docx，再用 Word 按页定位后删除前部。

需要：Windows + Microsoft Word + pywin32。

说明：分页以 Word 当前版式下的页统计为准（ComputeStatistics(wdStatisticPages)）。
若文档含复杂分节，裁切后首页可能变为新文档的第 1 页，属预期行为。
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

WD_GOTO_PAGE = 1
WD_GOTO_ABSOLUTE = 1
WD_STATISTIC_PAGES = 2


def main() -> int:
    parser = argparse.ArgumentParser(description="保留 Word 文档最后 N 页（删前部）")
    parser.add_argument("source", type=Path, help="原始 docx，如 封面.docx")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="输出路径（默认：同目录 「原名_最后N页.docx」）",
    )
    parser.add_argument(
        "-n",
        "--pages",
        type=int,
        default=2,
        help="保留最后几页（默认 2）",
    )
    args = parser.parse_args()

    if not args.source.is_file():
        print(f"找不到: {args.source}", file=sys.stderr)
        return 1
    if args.pages < 1:
        print("pages 至少为 1", file=sys.stderr)
        return 1

    out = args.output
    if out is None:
        out = args.source.parent / f"{args.source.stem}_最后{args.pages}页.docx"

    try:
        import win32com.client  # type: ignore
    except ImportError:
        print("需要安装 pywin32: pip install pywin32", file=sys.stderr)
        return 1

    work = out.parent / f".extract_last_pages_work_{out.stem}.docx"
    try:
        shutil.copy2(args.source, work)
    except OSError as e:
        print(f"复制失败: {e}", file=sys.stderr)
        return 1

    word = None
    doc = None
    save_path = out
    total_pages: int | None = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(str(work.resolve()), False, False, False)

        total_pages = int(doc.ComputeStatistics(WD_STATISTIC_PAGES))
        if total_pages < args.pages:
            print(
                f"警告: 文档仅有 {total_pages} 页，小于请求的 {args.pages} 页，将保留全部内容。",
                file=sys.stderr,
            )
            first_keep = 1
        else:
            first_keep = total_pages - args.pages + 1

        if first_keep > 1:
            keep_anchor = doc.GoTo(WD_GOTO_PAGE, WD_GOTO_ABSOLUTE, first_keep)
            cut_end = int(keep_anchor.Start) - 1
            start_pos = int(doc.Content.Start)
            if cut_end >= start_pos:
                doc.Range(start_pos, cut_end).Delete()

        if save_path.is_file():
            try:
                save_path.unlink()
            except OSError:
                save_path = out.parent / f"{out.stem}_新{out.suffix}"
                print(
                    f"提示: {out.name} 被占用，已改为写入 {save_path.name}",
                    file=sys.stderr,
                )
        doc.SaveAs2(str(save_path.resolve()))
    except Exception as exc:
        print(f"Word 处理失败: {exc}", file=sys.stderr)
        return 1
    finally:
        if doc is not None:
            doc.Close(False)
        if word is not None:
            word.Quit()
        try:
            work.unlink(missing_ok=True)
        except OSError:
            pass

    tp = total_pages if total_pages is not None else "?"
    print(
        f"已写入: {save_path.resolve()}（来源 {args.source.name}；分页统计原约 {tp} 页 → 输出仅含末尾 {args.pages} 页对应内容）"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
