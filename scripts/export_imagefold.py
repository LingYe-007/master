#!/usr/bin/env python3
"""Export thesis figures and table screenshots into imagefold/."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "imagefold"
FIG_OUT = OUT / "figures"
TAB_OUT = OUT / "tables"

# figure: (label, chapter, caption_short, source_path relative to ROOT)
FIGURES = [
    ("fig:framework", "ch01", "论文结构", "images/论文结构.png"),
    ("fig:bipartite_matrix", "ch02", "二部图与交互矩阵", "images/bipartite_matrix.png"),
    ("fig:gnn", "ch02", "图神经网络", "images/图神经网络.png"),
    ("fig:homo_hetero_graph", "ch02", "同构图与异构图对比", "images/同构图与异构图对比.png"),
    ("fig:meta_path", "ch02", "元路径", "images/元路径.png"),
    ("fig:hypergraph_compare", "ch02", "超图对比", "images/hypergraph_compare.png"),
    ("fig:fl_overview", "ch02", "联邦学习", "images/联邦学习.png"),
    ("fig:horizontal_vertical_fl", "ch02", "横向纵向联邦", "images/horizontal_vertical_fl.png"),
    ("fig:fed_prototype_align", "ch02", "联邦原型对齐", "images/fed_prototype_fl_flow.png"),
    ("fig:fedascl_framework", "ch03", "FedASCL框架", "images/fedascl_framework.png"),
    ("fig:attr_semantic_build", "ch03", "属性语义图构建", "images/属性语义图构建.png"),
    ("fig:cross_view_cl", "ch03", "跨视图对比机制", "images/跨视图对比机制.png"),
    ("fig:prototype_alignment", "ch03", "基于原型的语义对齐", "images/基于原型的语义对齐策略.png"),
    ("fig:training_progress", "ch03", "训练收敛曲线", "images/experiment.png"),
    ("fig:noniidplot", "ch03", "Non-IID鲁棒性", "images/non_iid_robustness.png"),
    ("fig:compression_framework", "ch04", "压缩上传流程", "images/fedascl上传阶段.png"),
    ("fig:selector_logic", "ch04", "元路径选择器", "images/selector_logic.png"),
    ("fig:ablation", "ch04", "压缩消融实验", "images/ablation_study.png"),
    ("fig:sys_arch", "ch05", "系统架构图", "images/系统架构图.png"),
    ("fig:storage_layer", "ch05", "用户子图存储", "images/用户子图示意图.png"),
    ("fig:sys_tech_flow", "ch05", "系统主要组件", "images/系统主要组件.png"),
    ("fig:simulator_arch", "ch05", "联邦仿真引擎", "images/联邦学习仿真引擎架构图.png"),
    ("fig:ui_settings", "ch05", "个人设置页面", "images/个人设置页面.png"),
    ("fig:ui_monitor", "ch05", "训练监控面板", "images/中央服务器训练面板.png"),
]

# table: (label, chapter, caption keyword for PDF search)
TABLES = [
    ("tab:federated_cold_llm_compare", "ch01", "联邦冷启动场景下传统图联邦推荐与大模型联邦推荐的主要差异"),
    ("tab:dataset_stat", "ch03", "实验数据集统计信息"),
    ("tab:dataset_attr_ml", "ch03", "MovieLens-1M 数据集属性字段及编码方式"),
    ("tab:dataset_attr_yelp", "ch03", "Yelp 数据集属性字段及编码方式"),
    ("tab:dataset_attr_acm", "ch03", "ACM 数据集属性字段及编码方式"),
    ("tab:exp_config_chap3", "ch03", "第三章实验配置汇总"),
    ("tab:overall_performance", "ch03", "各算法在三个数据集上的总体性能对比"),
    ("tab:cold_start_res", "ch03", "冷启动用户场景下的性能对比"),
    ("tab:non_iid_data", "ch03", "性能鲁棒性对比"),
    ("tab:ablation", "ch03", "消融实验结果"),
    ("tab:exp_config_chap4", "ch04", "第四章实验配置汇总"),
    ("tab:performance_comparison", "ch04", "不同压缩策略下的推荐性能对比"),
    ("tab:compression_tradeoff", "ch04", "代表性压缩配置下的通信与精度对照"),
    ("tab:communication_cost", "ch04", "通信开销对比"),
    ("tab:tech_stack", "ch05", "系统技术选型与开发环境"),
    ("tab:func_test", "ch05", "系统主要功能测试用例及结果"),
]


def safe_name(s: str) -> str:
    s = re.sub(r'[\\/:*?"<>|]', "_", s)
    return s[:80]


def copy_figures() -> list[str]:
    FIG_OUT.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for idx, (label, chapter, short, rel) in enumerate(FIGURES, 1):
        src = ROOT / rel
        stem = label.replace(":", "_")
        dst_name = f"{idx:02d}_{chapter}_{stem}_{safe_name(short)}{src.suffix}"
        dst = FIG_OUT / dst_name
        if not src.exists():
            lines.append(f"- [缺失] {label} <- {rel}")
            continue
        shutil.copy2(src, dst)
        lines.append(f"- {label} -> figures/{dst_name}")
    return lines


def find_table_rect(page: fitz.Page, keyword: str) -> fitz.Rect | None:
    """Locate table region by caption keyword on page."""
    blocks = page.get_text("blocks")
    caption_y = None
    for b in blocks:
        if keyword in b[4]:
            caption_y = b[1]
            break
    if caption_y is None:
        return None
    # crop from slightly above caption to page bottom (table usually below caption)
    r = page.rect
    top = max(r.y0, caption_y - 12)
    return fitz.Rect(r.x0 + 36, top, r.x1 - 36, r.y1 - 36)


def export_tables(pdf_path: Path) -> list[str]:
    TAB_OUT.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    if not pdf_path.exists():
        return [f"- [跳过] PDF 不存在: {pdf_path}"]

    doc = fitz.open(pdf_path)
    mat = fitz.Matrix(2.5, 2.5)

    for idx, (label, chapter, keyword) in enumerate(TABLES, 1):
        stem = label.replace(":", "_")
        dst = TAB_OUT / f"{idx:02d}_{chapter}_{stem}.png"
        found = False
        for page in doc:
            if keyword not in page.get_text():
                continue
            rect = find_table_rect(page, keyword)
            if rect is None:
                pix = page.get_pixmap(matrix=mat, alpha=False)
            else:
                pix = page.get_pixmap(matrix=mat, clip=rect, alpha=False)
            pix.save(dst)
            lines.append(f"- {label} -> tables/{dst.name} (caption: {keyword[:24]}…)")
            found = True
            break
        if not found:
            lines.append(f"- [未找到] {label} (caption: {keyword})")

    doc.close()
    return lines


def write_index(fig_lines: list[str], tab_lines: list[str]) -> None:
    content = """# 论文图表汇总 (imagefold)

本目录由 `scripts/export_imagefold.py` 自动生成，包含正文引用的全部图（原图复制）与表（自 PDF 裁剪截图）。

## 图 (figures/)

"""
    content += "\n".join(fig_lines) + "\n\n## 表 (tables/)\n\n"
    content += "\n".join(tab_lines) + "\n"
    (OUT / "README.md").write_text(content, encoding="utf-8")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    fig_lines = copy_figures()
    pdf = ROOT / "main.pdf"
    if not pdf.exists():
        pdf = ROOT / "output" / "main.pdf"
    tab_lines = export_tables(pdf)
    write_index(fig_lines, tab_lines)

    n_fig = len(list(FIG_OUT.glob("*")))
    n_tab = len(list(TAB_OUT.glob("*")))
    print(f"Done: {OUT}")
    print(f"  figures: {n_fig}")
    print(f"  tables:  {n_tab}")


if __name__ == "__main__":
    main()
