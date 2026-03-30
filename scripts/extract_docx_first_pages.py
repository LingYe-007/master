#!/usr/bin/env python3
"""
从完整封面 Word 文档中保留前 N 页，不采用“新建文档再粘贴”（易丢节/页眉页脚/页面设置）。
做法：先复制整份 docx，再在副本中删除「第 N+1 页起点」之后的全部内容，版面与原文档一致。
需要：Windows + Microsoft Word + pywin32。
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# Word GoTo: wdGoToPage=1, wdGoToAbsolute=1
WD_GOTO_PAGE = 1
WD_GOTO_ABSOLUTE = 1


def main() -> int:
    parser = argparse.ArgumentParser(description="保留 Word 文档前 N 页（删后部，保全版面设置）")
    parser.add_argument("source", type=Path, help="原始 docx，如 封面.docx")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="输出路径（默认：同目录 封面_前六页.docx 或 source 加 _前N页）",
    )
    parser.add_argument("-n", "--pages", type=int, default=6, help="保留前几页（默认 6）")
    args = parser.parse_args()

    if not args.source.is_file():
        print(f"找不到: {args.source}", file=sys.stderr)
        return 1
    if args.pages < 1:
        print("pages 至少为 1", file=sys.stderr)
        return 1

    out = args.output
    if out is None:
        out = args.source.parent / f"{args.source.stem}_前{args.pages}页.docx"

    try:
        import win32com.client  # type: ignore
    except ImportError:
        print("需要安装 pywin32: pip install pywin32", file=sys.stderr)
        return 1

    work = out.parent / f".extract_cover_work_{out.stem}.docx"
    try:
        shutil.copy2(args.source, work)
    except OSError as e:
        print(f"复制失败: {e}", file=sys.stderr)
        return 1

    word = None
    doc = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(str(work.resolve()), False, False, False)
        save_path = out
        # 始终以「第 N+1 页起点」裁切（不依赖 ComputeStatistics，其易与屏幕分页不一致）
        first_remove = doc.GoTo(WD_GOTO_PAGE, WD_GOTO_ABSOLUTE, args.pages + 1)
        end_pos = doc.Content.End
        start_del = int(first_remove.Start)
        if start_del < end_pos - 1:
            doc.Range(start_del, end_pos).Delete()
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

    print(f"已写入: {save_path.resolve()}（保留前 {args.pages} 页，版式继承自 {args.source.name}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
