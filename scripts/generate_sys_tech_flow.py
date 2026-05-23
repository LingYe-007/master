#!/usr/bin/env python3
"""Generate system technical stack diagram for thesis chapter 5."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images" / "sys_tech_flow.png"

# Layer: (title, detail, fill, edge)
LAYERS = [
    (
        "展示层",
        "React + TypeScript + ECharts",
        "#E8F4FC",
        "#2B6CB0",
    ),
    (
        "服务与调度层",
        "Flask（API）+ Celery（异步联邦任务）+ Redis（队列与热状态）",
        "#E8F8EE",
        "#2F855A",
    ),
    (
        "算法与训练运行时",
        "Python 3.8 / PyTorch / PyG（FedASCL 与压缩上传）",
        "#FFF8E8",
        "#C05621",
    ),
    (
        "持久化层",
        "MySQL（全局元数据与账号）  +  客户端 SQLite（本地子图与属性）",
        "#F3EEFA",
        "#6B46C1",
    ),
]

CONN_LABELS = ["REST / HTTPS", "", "", ""]


def pick_font():
    from matplotlib import font_manager

    candidates = [
        "PingFang SC",
        "Heiti SC",
        "STHeiti",
        "Songti SC",
        "Noto Sans CJK SC",
        "Arial Unicode MS",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            return name
    return "sans-serif"


def main():
    font = pick_font()
    plt.rcParams["font.sans-serif"] = [font, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    fig_w, fig_h = 10.5, 7.2
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=200)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 7.2)
    ax.axis("off")

    box_w = 9.2
    box_h = 1.05
    x0 = (10.5 - box_w) / 2
    top_y = 6.0
    gap = 0.42

    y = top_y
    centers = []
    for title, detail, fill, edge in LAYERS:
        box = FancyBboxPatch(
            (x0, y - box_h),
            box_w,
            box_h,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            linewidth=1.2,
            edgecolor=edge,
            facecolor=fill,
        )
        ax.add_patch(box)
        cy = y - box_h / 2
        centers.append(cy)
        ax.text(
            10.5 / 2,
            cy + 0.18,
            title,
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color="#1A202C",
        )
        ax.text(
            10.5 / 2,
            cy - 0.22,
            detail,
            ha="center",
            va="center",
            fontsize=10,
            color="#2D3748",
        )
        y -= box_h + gap

    for i in range(len(centers) - 1):
        y1 = centers[i] - box_h / 2 - 0.06
        y2 = centers[i + 1] + box_h / 2 + 0.06
        arrow = FancyArrowPatch(
            (10.5 / 2, y1),
            (10.5 / 2, y2),
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=1.4,
            color="#4A5568",
        )
        ax.add_patch(arrow)
        label = CONN_LABELS[i]
        if label:
            mid = (y1 + y2) / 2
            ax.text(
                10.5 / 2 + 0.15,
                mid,
                label,
                ha="left",
                va="center",
                fontsize=9.5,
                color="#4A5568",
                style="italic",
            )

    fig.savefig(OUT, bbox_inches="tight", facecolor="white", pad_inches=0.15)
    plt.close(fig)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
