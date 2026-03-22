#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
绘制 FedASCL 算法总体架构示意图（依据论文 chap3 3.2 节六步流程）
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Circle, RegularPolygon
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(PROJECT_ROOT, 'images')
os.makedirs(OUT_DIR, exist_ok=True)


def _get_chinese_font():
    for name in ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Heiti SC', 'STHeiti']:
        if any(f.name == name for f in fm.fontManager.ttflist):
            return name
    return None


def draw_simple_graph(ax, cx, cy, w, h, color, edgecolor):
    """在给定区域内绘制简易网络图（节点+边）"""
    nodes = [(cx - w*0.25, cy + h*0.2), (cx + w*0.25, cy + h*0.2),
             (cx - w*0.2, cy - h*0.2), (cx + w*0.2, cy - h*0.2)]
    for (nx, ny) in nodes:
        circ = Circle((nx, ny), 0.08, facecolor=color, edgecolor=edgecolor, lw=0.8)
        ax.add_patch(circ)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            ax.plot([nodes[i][0], nodes[j][0]], [nodes[i][1], nodes[j][1]],
                    color=edgecolor, lw=0.8, alpha=0.9, zorder=1)


def draw_cloud_shape(ax, cx, cy, w, h, facecolor, edgecolor):
    """绘制云形"""
    r = min(w, h) * 0.2
    centers = [(cx - w*0.2, cy), (cx, cy + h*0.15), (cx + w*0.2, cy),
               (cx - w*0.1, cy - h*0.1), (cx + w*0.1, cy - h*0.1)]
    for (ox, oy) in centers:
        c = Circle((ox, oy), r, facecolor=facecolor, edgecolor=edgecolor, lw=1.2)
        ax.add_patch(c)


def draw_magnifier(ax, cx, cy, r, edgecolor):
    """绘制简易放大镜图标（用于跨视图对比模块）"""
    # 镜片圆
    c = Circle((cx - r*0.15, cy + r*0.15), r*0.5, facecolor='none', edgecolor=edgecolor, lw=1.2)
    ax.add_patch(c)
    # 手柄
    handle_x = cx - r*0.15 + r*0.5*0.7
    handle_y = cy + r*0.15 - r*0.5*0.7
    ax.plot([handle_x, handle_x + r*0.8], [handle_y, handle_y - r*0.8], color=edgecolor, lw=1.2)


def draw_gear_shape(ax, cx, cy, r, edgecolor):
    """绘制简易齿轮（圆+放射线）"""
    c = Circle((cx, cy), r, facecolor='white', edgecolor=edgecolor, lw=1, alpha=0.9)
    ax.add_patch(c)
    for i in range(8):
        th = i * 2 * np.pi / 8
        ax.plot([cx + r*0.7*np.cos(th), cx + r*np.cos(th)],
                [cy + r*0.7*np.sin(th), cy + r*np.sin(th)], color=edgecolor, lw=1)


def draw_hexagon(ax, cx, cy, r, facecolor, edgecolor):
    """绘制六边形（平顶）"""
    h = RegularPolygon((cx, cy), numVertices=6, radius=r, orientation=np.pi/2,
                       facecolor=facecolor, edgecolor=edgecolor, linewidth=1.2)
    ax.add_patch(h)


def polyline_arrow(ax, waypoints, color='#333', lw=1.2, head_size=0.15, ls='-', alpha=1.0):
    """绘制折线箭头（纯直线段）"""
    waypoints = list(waypoints)
    if len(waypoints) < 2:
        return
    xs, ys = zip(*waypoints)
    ax.plot(xs, ys, color=color, lw=lw, linestyle=ls, alpha=alpha)
    x1, y1 = waypoints[-2]
    x2, y2 = waypoints[-1]
    dx, dy = x2 - x1, y2 - y1
    L = np.hypot(dx, dy) or 1e-6
    ux, uy = dx / L, dy / L
    ax.annotate('', xy=(x2, y2), xytext=(x2 - head_size * ux, y2 - head_size * uy),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw, alpha=alpha))


def draw_fedascl_framework(params=None):
    """绘制框架图。params: dict，如 {'dpi':250,'figscale':1.0}，用于优化循环"""
    p = params or {}
    dpi = p.get('dpi', 250)
    figscale = p.get('figscale', 1.0)
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(14 * figscale, 9 * figscale))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')

    # 配色（按参考图：服务端灰、语义蓝、结构橙、原型绿）
    panel_bg = '#eeeeee'      # 分区背景（浅灰面板）
    gray_bg = '#f5f5f5'
    blue_fill = '#e3f2fd'     # 属性语义图（蓝）
    blue_edge = '#1976d2'
    orange_fill = '#fff3e0'   # 交互结构图（橙）
    orange_edge = '#e65100'
    green_fill = '#e8f5e9'    # 原型对齐、语义编码器（绿）
    green_edge = '#2e7d32'
    white_fill = '#ffffff'
    gray_box = '#e8e8e8'      # 流程框
    text_dark = '#333333'

    def box(x, y, w, h, text, fc=white_fill, ec=text_dark, fs=9):
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.1",
                           facecolor=fc, edgecolor=ec, linewidth=1.2)
        ax.add_patch(b)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fs)

    def arrow(x1, y1, x2, y2, color=text_dark):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.2))

    # ========== A. 服务端 (Server) ==========
    ax.add_patch(FancyBboxPatch((0.2, 8.4), 13.6, 1.4, boxstyle="round,pad=0.04",
                               facecolor=panel_bg, edgecolor='#999', linewidth=1.2))
    ax.text(0.6, 9.1, 'A.', fontsize=11, fontweight='bold')
    ax.text(7, 9.1, '服务端 (Global / Server)', ha='center', fontsize=11, fontweight='bold')

    # 蓝云：全局语义原型聚合
    draw_cloud_shape(ax, 3.5, 8.95, 2.2, 0.7, blue_fill, blue_edge)
    ax.text(3.5, 8.95, '全局语义原型聚合\nPrototypes Aggregation', ha='center', va='center', fontsize=8)
    # 橙云+齿轮：模型聚合(加权平均)
    draw_cloud_shape(ax, 10.5, 8.95, 2.2, 0.7, orange_fill, orange_edge)
    draw_gear_shape(ax, 10.5, 8.95, 0.2, orange_edge)
    ax.text(10.5, 8.95, '模型聚合 (加权平均)\nModel Aggregation (Weighted Average)', ha='center', va='center', fontsize=8)
    arrow(5.7, 8.95, 8.3, 8.95)  # 蓝云->橙云

    # ========== B. 客户端 (风格对齐论文：冷启动推荐策略、跨视图对比等) ==========
    ax.add_patch(FancyBboxPatch((0.4, 0.3), 13.2, 7.9, boxstyle="round,pad=0.05",
                               facecolor='#eeeeee', edgecolor='#888', linewidth=1.5))
    ax.text(7, 8.0, 'B. 客户端 (Local / Client)', ha='center', fontsize=11, fontweight='bold')

    ax.add_patch(FancyBboxPatch((0.7, 0.6), 12.6, 7.0, boxstyle="round,pad=0.02",
                               facecolor='none', edgecolor='#999', linewidth=1.5, linestyle='--'))
    # 流程概览（与 fed_prototype_align 顶部流程条风格一致）
    ax.text(7, 7.75, '双视图构建 → 编码 → 对比 → 原型对齐 → 聚合 → 联合优化', ha='center', fontsize=8, style='italic')
    ax.text(7, 0.4, 'Iterative Local Training', ha='center', fontsize=10, style='italic')

    # --- 1. 双视图输入 ---
    box(1.0, 6.1, 1.8, 0.55, '用户/物品 Raw 原始属性', gray_box)
    box(1.0, 5.0, 1.8, 0.55, '本地 Interaction 数据', gray_box)

    ax.add_patch(FancyBboxPatch((3.0, 5.0), 3.0, 2.2, boxstyle="round,pad=0.02",
                               facecolor='none', edgecolor='#999', lw=1, linestyle='--'))
    ax.text(4.5, 7.05, 'Graph Construction', ha='center', fontsize=9, style='italic')

    # 属性语义图、交互结构图：六边形
    g1_cx, g1_cy, g1_r = 3.85, 6.3, 0.5
    draw_hexagon(ax, g1_cx, g1_cy, g1_r, blue_fill, blue_edge)
    draw_simple_graph(ax, g1_cx, g1_cy, 0.5, 0.4, blue_fill, blue_edge)
    ax.text(g1_cx, 5.55, '属性语义图 kNN\nSemantic Graph', ha='center', fontsize=8)

    g2_cx, g2_cy, g2_r = 3.85, 5.3, 0.5
    draw_hexagon(ax, g2_cx, g2_cy, g2_r, orange_fill, orange_edge)
    draw_simple_graph(ax, g2_cx, g2_cy, 0.5, 0.4, orange_fill, orange_edge)
    ax.text(g2_cx, 4.55, '交互结构图\nStructural Graph', ha='center', fontsize=8)

    ax.text(4.5, 4.85, '1. 双视图输入', ha='center', fontsize=8)
    arrow(2.8, 6.35, 3.35, 6.3)
    arrow(2.8, 5.25, 3.35, 5.3)

    # --- 2. 双视图编码（语义编码器浅绿、结构编码器浅橙）---
    box(6.8, 6.5, 1.6, 0.5, '异构GNN编码器\nGNN Encoder', green_fill, green_edge)
    box(6.8, 5.5, 1.6, 0.5, '异构GNN编码器\nGNN Encoder', orange_fill, orange_edge)
    arrow(4.35, 6.3, 6.8, 6.75)
    arrow(4.35, 5.3, 6.8, 5.75)

    box(8.8, 6.75, 1.5, 0.35, '语义节点表示 Representations', gray_box)
    box(8.8, 5.75, 1.5, 0.35, '结构节点表示 Representations', gray_box)
    arrow(8.4, 6.75, 8.8, 6.92)
    arrow(8.4, 5.75, 8.8, 5.92)
    ax.text(7.8, 5.95, '2. 双视图编码', ha='center', fontsize=8)

    # --- 3. 跨视图对比（带放大镜图标，与跨视图对比机制图风格一致）---
    cl_x, cl_y = 8.8, 4.5
    ax.add_patch(FancyBboxPatch((cl_x - 1.3, cl_y - 0.4), 2.6, 0.8, boxstyle="round,pad=0.03",
                               facecolor=white_fill, edgecolor=text_dark, lw=1.2))
    draw_magnifier(ax, cl_x - 1.0, cl_y + 0.15, 0.2, text_dark)  # 放大镜图标
    ax.text(cl_x, cl_y, '3. 跨视图对比 Contrastive\n(最大化互信息 Maximize Mutual Information)',
            ha='center', va='center', fontsize=7)
    arrow(8.8, 5.92, 8.5, 4.9)
    arrow(8.8, 6.57, 8.2, 4.9)

    # --- 4. 原型对齐（绿色框）---
    box(11.2, 3.8, 1.9, 0.6, '4. 原型对齐 (修正偏差)\n4. Prototype Alignment (Correct Non-IID Bias)', green_fill, green_edge)
    arrow(9.5, 5.75, 10.5, 4.1)
    arrow(10.0, 4.9, 11.0, 4.1)

    # --- 元路径 & 推荐（元路径挖掘蓝、推荐预测浅蓝）---
    box(11.2, 6.2, 1.9, 0.55, '元路径挖掘 Mining &\n注意力融合 Attention Weights', blue_fill, blue_edge)
    box(13.0, 6.2, 1.0, 0.5, 'Recommendation\nPrediction', blue_fill, blue_edge)
    arrow(9.5, 6.75, 11.0, 6.45)
    arrow(9.5, 4.9, 10.8, 5.5)
    arrow(12.2, 6.45, 13.0, 6.45)
    ax.text(11.8, 6.55, 'Meta-paths\nAttention', fontsize=6, alpha=0.9)

    # --- 5. 损失计算（Rec Loss Main + CL Loss Aux，参考图两组件）---
    loss_y = 2.5
    box(11.2, loss_y + 0.5, 0.6, 0.4, 'Rec Loss\n(Main Task)', gray_box, fs=6)
    box(11.85, loss_y + 0.5, 0.6, 0.4, 'CL Loss\n(Auxiliary Task)', gray_box, fs=6)
    box(12.5, loss_y + 0.5, 0.55, 0.4, 'Proto\n(Aux)', gray_box, fs=6)
    ax.add_patch(FancyBboxPatch((11.2, loss_y - 0.15), 1.9, 1.05, boxstyle="round,pad=0.02",
                               facecolor=white_fill, edgecolor=text_dark, lw=1.2))
    ax.text(12.15, loss_y + 0.2, '5. 损失计算 Loss Calculation (L_total=L_rec+λ1·L_cl+λ2·L_proto)', ha='center', fontsize=7)
    arrow(12.5, 5.95, 12.0, loss_y + 0.9)
    arrow(10.5, 4.1, 11.5, loss_y + 0.9)

    # --- 6. 联合优化（蓝框，输出 Updated Model Parameters）---
    box(11.2, 1.5, 1.9, 0.55, '6. 联合反向传播与参数更新\n6. Joint Optimization', blue_fill, blue_edge)
    arrow(12.15, 2.5, 12.15, 2.08)
    arrow(11.2, 2.6, 11.2, 2.08)

    # ========== 端云箭头 ==========
    polyline_arrow(ax, [(3.5, 8.5), (3.5, 4.5), (10.8, 4.5), (10.8, 4.3)],
                  color=blue_edge, lw=1.5, head_size=0.2)
    ax.text(6.0, 6.8, 'Global Prototypes', ha='center', fontsize=8)

    polyline_arrow(ax, [(11.2, 1.2), (11.2, 8.5), (10.5, 8.5)],
                  color=orange_edge, lw=1.5, head_size=0.2)
    ax.text(11.5, 4.5, 'Updated Model\nParameters', ha='center', fontsize=8)

    polyline_arrow(ax, [(11.0, 4.0), (7.0, 4.0), (7.0, 8.5), (3.5, 8.5)],
                  color=blue_edge, lw=1.2, head_size=0.18, ls='--', alpha=0.85)
    ax.text(8.0, 6.2, 'Local Prototypes', ha='center', fontsize=7)

    # Global Model Update 指向「用户/物品 Raw 原始属性」
    polyline_arrow(ax, [(10.5, 8.5), (2.0, 8.5), (2.0, 6.4), (1.9, 6.375)],
                  color='#666', lw=1.2, head_size=0.18, ls='--')
    ax.text(5.5, 7.5, 'Global Model Update', fontsize=7)

    fig.tight_layout()
    out_path = os.path.join(OUT_DIR, 'fedascl_framework.png')
    fig.savefig(out_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Saved: {out_path}')
    return out_path


if __name__ == '__main__':
    draw_fedascl_framework()
    print('Done.')
