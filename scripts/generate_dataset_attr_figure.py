#!/usr/bin/env python3
"""Generate dataset attribute overview figure for thesis."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images" / "dataset_attr_overview.png"

BLOCKS = [
    (
        "MovieLens-1M",
        "#E8F4FC",
        "#2B6CB0",
        [
            ("用户节点", "Gender 性别(M/F)", "Age 年龄(7档)", "Occupation 职业(21类)"),
            ("", "编码: One-hot 后拼接", "", ""),
            ("物品节点(电影)", "Genres 影片类型(19类,多标签)", "", ""),
            ("", "编码: Multi-hot(19维)", "Zip-code/片名未纳入", ""),
        ],
    ),
    (
        "Yelp",
        "#E8F8EE",
        "#2F855A",
        [
            ("用户节点", "average_stars 平均评分", "review_count 评论数", "useful/funny/cool"),
            ("", "fans 粉丝数", "elite 精英用户标记", ""),
            ("", "编码: 离散 One-hot, 连续 Min-Max", "", ""),
            ("商户节点", "categories 类别(多值)", "stars 星级", "review_count"),
            ("", "city/state 城市州", "latitude/longitude", "is_open"),
            ("", "编码: 类别 Multi-hot, 其余归一化", "", ""),
        ],
    ),
    (
        "ACM",
        "#F3EEFA",
        "#6B46C1",
        [
            ("作者节点", "author_id 作者编号", "name 姓名", "affiliation 所属机构"),
            ("", "interests 研究兴趣", "research_direction 研究方向", "keywords/subject"),
            ("", "编码: 多标签 Multi-hot, 机构/学科 One-hot", "", ""),
            ("论文节点", "title 标题", "venue 会议/期刊", "year 年份"),
            ("", "abstract 摘要", "keywords 关键词", "subject 学科"),
            ("", "编码: 关键词 Multi-hot, 年份 Min-Max, 文本字段 TF-IDF/嵌入", "", ""),
            ("系统对应", "个人设置页画像字段", "推荐列表论文元数据", "U-P-A-P / U-P-K-P"),
        ],
    ),
]


def pick_font():
    from matplotlib import font_manager

    for name in ["PingFang SC", "Heiti SC", "STHeiti", "Songti SC", "Arial Unicode MS"]:
        if name in {f.name for f in font_manager.fontManager.ttflist}:
            return name
    return "sans-serif"


def main():
    font = pick_font()
    plt.rcParams["font.sans-serif"] = [font, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, axes = plt.subplots(1, 3, figsize=(14, 5.2), dpi=200)
    for ax, (title, fill, edge, rows) in zip(axes, BLOCKS):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        box = FancyBboxPatch(
            (0.03, 0.03),
            0.94,
            0.94,
            boxstyle="round,pad=0.02,rounding_size=0.03",
            linewidth=1.2,
            edgecolor=edge,
            facecolor=fill,
        )
        ax.add_patch(box)
        ax.text(0.5, 0.92, title, ha="center", va="top", fontsize=12, fontweight="bold")
        y = 0.82
        for row in rows:
            if row[0]:
                ax.text(0.08, y, row[0], ha="left", va="top", fontsize=9, fontweight="bold", color="#1A202C")
                ax.text(0.32, y, "  ".join(x for x in row[1:] if x), ha="left", va="top", fontsize=8.5, color="#2D3748")
            else:
                ax.text(0.32, y, "  ".join(x for x in row[1:] if x), ha="left", va="top", fontsize=8.5, color="#4A5568")
            y -= 0.11

    fig.suptitle("三数据集属性视图所用真实字段概要", fontsize=13, fontweight="bold", y=1.02)
    fig.savefig(OUT, bbox_inches="tight", facecolor="white", pad_inches=0.12)
    plt.close(fig)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
