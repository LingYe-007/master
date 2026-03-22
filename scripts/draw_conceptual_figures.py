#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文概念图绘制：保持与 generate_figures / draw_fedascl_framework 统一的学术风格
配色：白底，#e3f2fd（浅蓝），#fff3e0（浅橙），#e8f5e9（浅绿），灰框 #e8e8e8
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(PROJECT_ROOT, 'images')
os.makedirs(OUT_DIR, exist_ok=True)

# 统一配色
BLUE_FILL = '#e3f2fd'
BLUE_EDGE = '#1565c0'
ORANGE_FILL = '#fff3e0'
ORANGE_EDGE = '#e65100'
GREEN_FILL = '#e8f5e9'
GRAY_BOX = '#e8e8e8'
TEXT_DARK = '#333333'
PANEL_BG = '#eeeeee'

# 全局字体规范（与 generate_figures 一致）
plt.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
})


def _get_chinese_font():
    for name in ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Heiti SC', 'STHeiti']:
        if any(f.name == name for f in fm.fontManager.ttflist):
            return name
    return None


def _arrow(ax, x1, y1, x2, y2, color=TEXT_DARK, ls='-'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.2, linestyle=ls))


def fig_paper_structure():
    """论文结构图：六章流程图（第一章...第六章）"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    chapters = [
        '第一章\n绪论', '第二章\n相关理论与技术', '第三章\nFedASCL框架',
        '第四章\n语义感知压缩', '第五章\n系统实现', '第六章\n总结与展望'
    ]
    x_centers = [1.5, 3.2, 4.9, 6.6, 8.0, 9.2]
    for i, (cx, label) in enumerate(zip(x_centers, chapters)):
        box = FancyBboxPatch((cx - 0.65, 2.5), 1.3, 1.2, boxstyle="round,pad=0.03",
                             facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, linewidth=1.2)
        ax.add_patch(box)
        ax.text(cx, 3.1, label, ha='center', va='center', fontsize=8)
        if i < len(chapters) - 1:
            _arrow(ax, cx + 0.65, 3.1, x_centers[i+1] - 0.65, 3.1)

    ax.text(5, 5.2, '本文研究框架', ha='center', fontsize=12, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '论文结构.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/论文结构.png')


def fig_bipartite_matrix():
    """用户-物品二部图与交互矩阵对应关系（含等价映射，与原图风格一致）"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    # 4x5 交互矩阵（与原图一致）
    mat = np.array([
        [1, 0, 1, 1, 0],
        [0, 1, 0, 1, 1],
        [1, 1, 1, 0, 0],
        [0, 0, 1, 1, 1],
    ])
    n_u, n_v = 4, 5

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5)
    ax.set_aspect('equal')
    ax.axis('off')

    # 左侧：交互矩阵
    ax.text(1.5, 4.2, '物品', ha='center', fontsize=11, fontweight='bold')
    for j in range(n_v):
        ax.text(2.2 + j * 0.75, 3.7, f'$v_{j+1}$', ha='center', fontsize=9)
    ax.text(0.4, 2.5, '用户', va='center', fontsize=11, fontweight='bold', rotation=90)
    for i in range(n_u):
        ax.text(0.9, 3.0 - i * 0.65, f'$u_{i+1}$', ha='right', va='center', fontsize=9)
    for i in range(n_u):
        for j in range(n_v):
            cx, cy = 2.2 + j * 0.75, 3.0 - i * 0.65
            if mat[i, j] == 1:
                box = FancyBboxPatch((cx - 0.28, cy - 0.28), 0.56, 0.56, boxstyle="round,pad=0.02",
                                     facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=0.8)
                ax.add_patch(box)
            else:
                ax.add_patch(Rectangle((cx - 0.28, cy - 0.28), 0.56, 0.56, fill=False, edgecolor='#cccccc', lw=0.5))

    # 中间：等价映射
    ax.annotate('', xy=(7.5, 2.5), xytext=(5.8, 2.5),
                arrowprops=dict(arrowstyle='<->', color=TEXT_DARK, lw=2))
    ax.text(6.65, 2.1, '等价映射', ha='center', fontsize=10, fontweight='bold')

    # 右侧：二部图
    u_y = [3.6, 2.8, 2.0, 1.2]
    v_y = [3.4, 2.6, 1.8, 1.0, 0.4]
    for i in range(n_u):
        c = Circle((9.5, u_y[i]), 0.18, facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1.2)
        ax.add_patch(c)
        ax.text(9.1, u_y[i], f'$u_{i+1}$', ha='right', va='center', fontsize=9)
    for j in range(n_v):
        c = Circle((12, v_y[j]), 0.18, facecolor=ORANGE_FILL, edgecolor=ORANGE_EDGE, lw=1.2)
        ax.add_patch(c)
        ax.text(12.4, v_y[j], f'$v_{j+1}$', ha='left', va='center', fontsize=9)
    for i in range(n_u):
        for j in range(n_v):
            if mat[i, j] == 1:
                ax.plot([9.5 + 0.18, 12 - 0.18], [u_y[i], v_y[j]], color=TEXT_DARK, lw=1, alpha=0.8)

    ax.text(7, 4.5, '用户-物品二部图与交互矩阵对应关系', ha='center', fontsize=11, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'bipartite_matrix.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/bipartite_matrix.png')


def fig_gnn():
    """图神经网络消息传递原理"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # 中心节点
    cx, cy = 4, 2.5
    c = Circle((cx, cy), 0.4, facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1.2)
    ax.add_patch(c)
    ax.text(cx, cy, '$u$', ha='center', va='center', fontsize=11)

    # 邻居
    neighbors = [(2, 1), (2, 4), (4, 4), (6, 4), (6, 1)]
    for nx, ny in neighbors:
        c = Circle((nx, ny), 0.25, facecolor=ORANGE_FILL, edgecolor=ORANGE_EDGE, lw=1)
        ax.add_patch(c)
        ax.plot([nx, cx], [ny, cy], color=TEXT_DARK, lw=1, alpha=0.7)

    ax.text(4, 4.5, 'AGGREGATE', ha='center', fontsize=9, style='italic')
    ax.text(4, 0.5, '$\\mathbf{e}_u^{(l)} = \\text{UPDATE}(\\mathbf{e}_u^{(l-1)}, \\mathbf{m}_{N_u})$', ha='center', fontsize=9)
    ax.text(4, 4.8, '图神经网络消息传递（Message Passing）', ha='center', fontsize=11, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '图神经网络.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/图神经网络.png')


def fig_homo_hetero():
    """同构图与异构图对比"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
    for ax in [ax1, ax2]:
        ax.set_xlim(0, 5)
        ax.set_ylim(0, 5)
        ax.set_aspect('equal')
        ax.axis('off')

    # 同构图：单一节点类型
    nodes = [(1, 2.5), (2.5, 4), (4, 2.5), (2.5, 1)]
    for n in nodes:
        c = Circle(n, 0.25, facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1)
        ax1.add_patch(c)
    for i in range(4):
        for j in range(i + 1, 4):
            ax1.plot([nodes[i][0], nodes[j][0]], [nodes[i][1], nodes[j][1]], color=TEXT_DARK, lw=1)
    ax1.set_title('同构图 (Homogeneous)\n单类型节点与边', fontsize=10)
    ax1.text(2.5, 0.3, '单一节点类型，单一边类型', ha='center', fontsize=9)

    # 异构图：多种节点
    u_nodes = [(1, 3.5), (1, 1.5)]
    v_nodes = [(3.5, 3.5), (3.5, 1.5), (4.5, 2.5)]
    for n in u_nodes:
        c = Circle(n, 0.22, facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1)
        ax2.add_patch(c)
        ax2.text(n[0] - 0.4, n[1], 'U', fontsize=8)
    for n in v_nodes:
        c = Circle(n, 0.22, facecolor=ORANGE_FILL, edgecolor=ORANGE_EDGE, lw=1)
        ax2.add_patch(c)
        ax2.text(n[0] + 0.35, n[1], 'V', fontsize=8)
    ax2.plot([1, 3.5], [3.5, 3.5], color=TEXT_DARK, lw=1)
    ax2.plot([1, 3.5], [1.5, 1.5], color=TEXT_DARK, lw=1)
    ax2.plot([1, 4.5], [2.5, 2.5], color=TEXT_DARK, lw=1)
    ax2.set_title('异构图 (Heterogeneous)\n多类型节点(U/V)与边', fontsize=10)
    ax2.text(2.5, 0.3, '多种节点类型，多种边/关系类型', ha='center', fontsize=9)

    fig.suptitle('同构图与异构图对比', fontsize=11, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '同构图与异构图对比.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/同构图与异构图对比.png')


def fig_meta_path():
    """元路径示意图：User-Author-Paper 等"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 4)
    ax.axis('off')

    # User - Author - Paper 路径
    u = Circle((1.5, 2), 0.3, facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1.2)
    ax.add_patch(u)
    ax.text(1.5, 2, 'U', ha='center', va='center')
    a1 = Circle((4, 2.5), 0.25, facecolor=ORANGE_FILL, edgecolor=ORANGE_EDGE, lw=1)
    ax.add_patch(a1)
    ax.text(4, 2.5, 'A', ha='center', va='center')
    p = Circle((6.5, 2), 0.25, facecolor=GREEN_FILL, edgecolor='#2e7d32', lw=1)
    ax.add_patch(p)
    ax.text(6.5, 2, 'P', ha='center', va='center')
    ax.plot([1.5, 4], [2, 2.5], 'k-', lw=1.2)
    ax.plot([4, 6.5], [2.5, 2], 'k-', lw=1.2)
    ax.text(2.75, 2.4, '$R_1$', fontsize=8)
    ax.text(5.25, 2.4, '$R_2$', fontsize=8)
    ax.text(4, 3.2, 'Meta-path: U $\\rightarrow$ A $\\rightarrow$ P', ha='center', fontsize=9)
    ax.text(4, 0.8, '元路径语义建模', ha='center', fontsize=10, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '元路径.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/元路径.png')


def fig_hypergraph_compare():
    """超图与普通图对比"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
    for ax in [ax1, ax2]:
        ax.set_xlim(0, 5)
        ax.set_ylim(0, 5)
        ax.set_aspect('equal')
        ax.axis('off')

    # 普通图：边连接 2 节点
    n1, n2, n3 = (1, 2.5), (2.5, 4), (4, 2.5)
    for n in [n1, n2, n3]:
        c = Circle(n, 0.2, facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1)
        ax1.add_patch(c)
    ax1.plot([n1[0], n2[0]], [n1[1], n2[1]], 'k-', lw=1.2)
    ax1.plot([n2[0], n3[0]], [n2[1], n3[1]], 'k-', lw=1.2)
    ax1.plot([n1[0], n3[0]], [n1[1], n3[1]], 'k-', lw=1.2)
    ax1.set_title('普通图 (Graph)\n边连接 2 个节点')

    # 超图：超边连接多节点
    n4, n5, n6 = (1.5, 2), (2.5, 3.5), (3.5, 2)
    for n in [n4, n5, n6]:
        c = Circle(n, 0.2, facecolor=ORANGE_FILL, edgecolor=ORANGE_EDGE, lw=1)
        ax2.add_patch(c)
    from matplotlib.patches import Polygon
    poly = Polygon([n4, n5, n6], fill=True, facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, alpha=0.5, linewidth=1.2)
    ax2.add_patch(poly)
    ax2.set_title('超图 (Hypergraph)\n超边连接 ≥2 节点')

    fig.suptitle('超图与普通图对比', fontsize=11, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'hypergraph_compare.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/hypergraph_compare.png')


def fig_federated_learning():
    """联邦学习架构：客户端-服务器"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # 服务器
    box = FancyBboxPatch((3.5, 4), 3, 1.2, boxstyle="round,pad=0.03",
                         facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1.2)
    ax.add_patch(box)
    ax.text(5, 4.6, 'Central Server\n模型聚合 / Model Aggregation', ha='center', va='center', fontsize=9)

    # 客户端
    clients = [(1, 1.5), (4, 1.5), (7, 1.5)]
    for i, (cx, cy) in enumerate(clients):
        box = FancyBboxPatch((cx - 0.6, cy - 0.5), 1.2, 1, boxstyle="round,pad=0.02",
                            facecolor=ORANGE_FILL, edgecolor=ORANGE_EDGE, lw=1)
        ax.add_patch(box)
        ax.text(cx, cy, f'Client {i+1}\n本地数据', ha='center', va='center', fontsize=8)
        _arrow(ax, cx, cy + 0.5, 4.5 + (i - 1) * 0.8, 4)
        _arrow(ax, 4.5 + (i - 1) * 0.8, 4, cx, cy + 0.5)

    ax.text(5, 5.5, '联邦学习架构（Client-Server）', ha='center', fontsize=11, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '联邦学习.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/联邦学习.png')


def fig_horizontal_vertical_fl():
    """横向联邦与纵向联邦数据分布对比"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
    for ax in [ax1, ax2]:
        ax.set_xlim(0, 5)
        ax.set_ylim(0, 5)
        ax.axis('off')

    # 横向：同特征不同用户
    ax1.add_patch(FancyBboxPatch((0.5, 2), 1.5, 2, facecolor=BLUE_FILL, edgecolor=BLUE_EDGE))
    ax1.add_patch(FancyBboxPatch((1.8, 2), 1.5, 2, facecolor=ORANGE_FILL, edgecolor=ORANGE_EDGE))
    ax1.add_patch(FancyBboxPatch((3.1, 2), 1.5, 2, facecolor=GREEN_FILL, edgecolor='#2e7d32'))
    ax1.text(1.25, 1.5, 'Client 1\nUsers A,B,C', ha='center', fontsize=8)
    ax1.text(2.55, 1.5, 'Client 2\nUsers D,E,F', ha='center', fontsize=8)
    ax1.text(3.85, 1.5, 'Client 3\nUsers G,H', ha='center', fontsize=8)
    ax1.set_title('横向联邦 (Horizontal FL)\n同特征空间，不同用户')

    # 纵向：同用户不同特征
    ax2.add_patch(FancyBboxPatch((0.5, 1.5), 4, 0.8, facecolor=BLUE_FILL, edgecolor=BLUE_EDGE))
    ax2.add_patch(FancyBboxPatch((0.5, 2.5), 4, 0.8, facecolor=ORANGE_FILL, edgecolor=ORANGE_EDGE))
    ax2.add_patch(FancyBboxPatch((0.5, 3.5), 4, 0.8, facecolor=GREEN_FILL, edgecolor='#2e7d32'))
    ax2.text(2.5, 1.9, 'Bank: 信用特征', ha='center', fontsize=8)
    ax2.text(2.5, 2.9, 'E-commerce: 消费特征', ha='center', fontsize=8)
    ax2.text(2.5, 3.9, 'Social: 社交特征', ha='center', fontsize=8)
    ax2.set_title('纵向联邦 (Vertical FL)\n同用户，不同特征')
    fig.suptitle('横向联邦与纵向联邦数据分布对比', fontsize=11, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'horizontal_vertical_fl.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/horizontal_vertical_fl.png')


def fig_contrastive_learning():
    """对比学习示意图：正负样本对"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # 输入 -> 增强1/增强2 -> 编码器 -> z1/z2
    ax.text(1.5, 2.5, '$x$', ha='center', fontsize=12)
    ax.text(3, 3.5, '$\\tilde{x}_1$', ha='center', fontsize=10)
    ax.text(3, 1.5, '$\\tilde{x}_2$', ha='center', fontsize=10)
    ax.text(5.5, 3.5, '$z_1$', ha='center', fontsize=10)
    ax.text(5.5, 1.5, '$z_2$', ha='center', fontsize=10)
    _arrow(ax, 1.5, 2.5, 2.5, 2.5)
    _arrow(ax, 2.5, 2.5, 3, 3.5)
    _arrow(ax, 2.5, 2.5, 3, 1.5)
    _arrow(ax, 3.5, 3.5, 5, 3.5)
    _arrow(ax, 3.5, 1.5, 5, 1.5)
    ax.plot([5.5, 5.5], [1.5, 3.5], 'k--', lw=1, alpha=0.7)
    ax.text(5.5, 2.5, '拉近', fontsize=8, ha='center')
    ax.text(4, 4.2, '对比学习：正样本对拉近，负样本对推远', ha='center', fontsize=10, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '对比学习.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/对比学习.png')


def fig_fed_prototype_align():
    """联邦原型聚合与语义对齐"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # 客户端上传本地原型
    for i, cx in enumerate([2, 5, 8]):
        box = FancyBboxPatch((cx - 0.7, 1.5), 1.4, 1, boxstyle="round,pad=0.02",
                             facecolor=ORANGE_FILL, edgecolor=ORANGE_EDGE, lw=1)
        ax.add_patch(box)
        ax.text(cx, 2, f'Client {i+1}\n本地原型', ha='center', va='center', fontsize=8)
        _arrow(ax, cx, 2.5, 5, 4.2)

    # 服务端聚合
    box = FancyBboxPatch((3.5, 4), 3, 1.2, boxstyle="round,pad=0.03",
                         facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1.2)
    ax.add_patch(box)
    ax.text(5, 4.6, 'Server: 全局原型聚合', ha='center', va='center', fontsize=9)

    _arrow(ax, 5, 4, 5, 3.2)
    ax.text(5.5, 3.6, '下发全局原型', fontsize=8)

    ax.text(5, 5.5, '联邦原型聚合与语义对齐', ha='center', fontsize=11, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'fed_prototype_align.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/fed_prototype_align.png')


def fig_attr_sem_graph():
    """属性语义图构建流程（A/B/C 三区结构，与原图风格一致）"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # A 区：属性处理与特征编码
    ax.add_patch(FancyBboxPatch((0.2, 3.2), 3.5, 2.2, boxstyle="round,pad=0.04", fill=False,
                                 edgecolor=BLUE_EDGE, lw=1, linestyle='--'))
    ax.text(1.95, 5.2, 'A. 属性处理与特征编码', fontsize=10, fontweight='bold')
    box1 = FancyBboxPatch((0.5, 3.8), 1.2, 0.6, boxstyle="round,pad=0.02", facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1)
    ax.add_patch(box1)
    ax.text(1.1, 4.1, 'User/Item\n原始属性', ha='center', va='center', fontsize=8)
    box2 = FancyBboxPatch((0.5, 3.2), 1.2, 0.5, boxstyle="round,pad=0.02", facecolor=GRAY_BOX, edgecolor=TEXT_DARK, lw=0.8)
    ax.add_patch(box2)
    ax.text(1.1, 3.45, 'One-Hot 编码', ha='center', va='center', fontsize=8)
    box3 = FancyBboxPatch((1.9, 3.2), 1.2, 0.5, boxstyle="round,pad=0.02", facecolor=GRAY_BOX, edgecolor=TEXT_DARK, lw=0.8)
    ax.add_patch(box3)
    ax.text(2.5, 3.45, 'Min-Max 归一化', ha='center', va='center', fontsize=8)
    _arrow(ax, 1.1, 3.8, 1.1, 3.7)
    _arrow(ax, 1.7, 3.45, 2.1, 3.45)
    box4 = FancyBboxPatch((2.2, 4.2), 1.0, 0.4, boxstyle="round,pad=0.02", facecolor=ORANGE_FILL, edgecolor=ORANGE_EDGE, lw=0.8)
    ax.add_patch(box4)
    ax.text(2.7, 4.4, 'Concat', ha='center', va='center', fontsize=8)
    ax.text(2.7, 3.9, '$\\mathbf{x}_v$', ha='center', va='center', fontsize=9)

    # B 区：属性语义相似度计算
    ax.add_patch(FancyBboxPatch((4.0, 3.2), 3.5, 2.2, boxstyle="round,pad=0.04", fill=False,
                                 edgecolor=ORANGE_EDGE, lw=1, linestyle='--'))
    ax.text(5.75, 5.2, 'B. 属性语义相似度计算', fontsize=10, fontweight='bold')
    box5 = FancyBboxPatch((4.5, 3.8), 2.5, 0.8, boxstyle="round,pad=0.02", facecolor=GRAY_BOX, edgecolor=TEXT_DARK, lw=1)
    ax.add_patch(box5)
    ax.text(5.75, 4.2, r'$S_{ij} = \frac{\mathbf{x}_i^\top \mathbf{x}_j}{\|\mathbf{x}_i\| \|\mathbf{x}_j\|}$', ha='center', va='center', fontsize=9)
    ax.text(5.75, 3.5, '相似度矩阵 $\\mathbf{S}$', ha='center', va='center', fontsize=9)
    _arrow(ax, 3.2, 4.0, 4.5, 4.0)

    # C 区：kNN 语义超图构建
    ax.add_patch(FancyBboxPatch((7.8, 1.5), 3.8, 3.2, boxstyle="round,pad=0.04", fill=False,
                                 edgecolor='#2e7d32', lw=1, linestyle='--'))
    ax.text(9.7, 4.5, 'C. kNN 语义超图构建', fontsize=10, fontweight='bold')
    steps_c = [
        (9.0, 3.8, 'Top-$k$ 相似节点选取'),
        (9.0, 3.0, '邻居集 $\\mathcal{N}_k(v_i)$'),
        (9.0, 2.2, '超图 $\\mathcal{G}=(\\mathcal{V},\\mathcal{E})$'),
        (9.0, 1.7, '关联矩阵 $H_{ve}$'),
    ]
    for i, (x, y, t) in enumerate(steps_c):
        box = FancyBboxPatch((8.0, y - 0.25), 2.2, 0.5, boxstyle="round,pad=0.02",
                             facecolor=GREEN_FILL, edgecolor='#2e7d32', lw=0.8)
        ax.add_patch(box)
        ax.text(x, y, t, ha='center', va='center', fontsize=8)
        if i < len(steps_c) - 1:
            _arrow(ax, x, y - 0.25, x, steps_c[i+1][1] + 0.25)
    _arrow(ax, 7.5, 3.5, 7.8, 3.5)
    ax.text(9.7, 1.0, '图神经网络输入', ha='center', fontsize=9, fontweight='bold')
    _arrow(ax, 9.7, 1.45, 9.7, 1.15)

    ax.text(6, 5.7, '属性语义图构建流程', ha='center', fontsize=11, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '属性语义图构建.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/属性语义图构建.png')


def fig_cross_view_cl():
    """跨视图对比机制"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # 双视图
    box1 = FancyBboxPatch((1, 2), 1.5, 1.2, boxstyle="round,pad=0.03",
                         facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1.2)
    ax.add_patch(box1)
    ax.text(1.75, 2.6, '属性视图\n$z^{attr}$', ha='center', va='center', fontsize=9)
    box2 = FancyBboxPatch((1, 0.5), 1.5, 1.2, boxstyle="round,pad=0.03",
                         facecolor=ORANGE_FILL, edgecolor=ORANGE_EDGE, lw=1.2)
    ax.add_patch(box2)
    ax.text(1.75, 1.1, '结构视图\n$z^{stru}$', ha='center', va='center', fontsize=9)

    # 对比模块
    box3 = FancyBboxPatch((4.5, 1), 2.5, 1.8, boxstyle="round,pad=0.03",
                         facecolor=GRAY_BOX, edgecolor=TEXT_DARK, lw=1.2)
    ax.add_patch(box3)
    ax.text(5.75, 1.9, 'InfoNCE / 最大化互信息', ha='center', va='center', fontsize=9)

    _arrow(ax, 2.5, 2.6, 4.5, 1.9)
    _arrow(ax, 2.5, 1.1, 4.5, 1.9)

    ax.text(5, 4.2, '跨视图对比学习机制', ha='center', fontsize=11, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '跨视图对比机制.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/跨视图对比机制.png')


def fig_prototype_alignment():
    """基于原型的语义对齐策略"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # 本地嵌入 -> 全局原型约束
    box1 = FancyBboxPatch((2, 2), 2, 1, boxstyle="round,pad=0.03",
                         facecolor=ORANGE_FILL, edgecolor=ORANGE_EDGE, lw=1.2)
    ax.add_patch(box1)
    ax.text(3, 2.5, '本地嵌入 $\\mathbf{z}_i$', ha='center', va='center', fontsize=9)
    box2 = FancyBboxPatch((5.5, 2), 2.5, 1, boxstyle="round,pad=0.03",
                         facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1.2)
    ax.add_patch(box2)
    ax.text(6.75, 2.5, '全局原型 $\\mathbf{c}_k$', ha='center', va='center', fontsize=9)
    box3 = FancyBboxPatch((4, 0.5), 2, 0.8, boxstyle="round,pad=0.02",
                         facecolor=GRAY_BOX, edgecolor=TEXT_DARK, lw=1)
    ax.add_patch(box3)
    ax.text(5, 0.9, '$\\mathcal{L}_{proto}$ 约束', ha='center', va='center', fontsize=9)

    _arrow(ax, 4, 2.5, 5, 2.5)
    _arrow(ax, 4.5, 2, 5, 0.9)

    ax.text(5, 4.2, '基于原型的语义对齐策略', ha='center', fontsize=11, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '基于原型的语义对齐策略.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/基于原型的语义对齐策略.png')


def fig_compression_flow():
    """压缩流程：评估-剪枝-量化-补偿"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    steps = [
        (1.5, 2.5, '1. 评估\n(注意力权重)'),
        (3.2, 2.5, '2. 剪枝\nTop-K 元路径'),
        (4.9, 2.5, '3. 量化\n低比特表示'),
        (6.6, 2.5, '4. 补偿\n误差累积'),
        (8.3, 2.5, '5. 上传'),
    ]
    for i, (x, y, t) in enumerate(steps):
        box = FancyBboxPatch((x - 0.65, y - 0.5), 1.3, 1.0, boxstyle="round,pad=0.03",
                             facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1.2)
        ax.add_patch(box)
        ax.text(x, y, t, ha='center', va='center', fontsize=8)
        if i < len(steps) - 1:
            _arrow(ax, x + 0.65, y, steps[i+1][0] - 0.65, y)

    ax.text(4.9, 4.2, '语义感知压缩流程（评估-剪枝-量化-补偿-上传）', ha='center', fontsize=11, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '压缩流程示意图.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/压缩流程示意图.png')


def fig_user_subgraph():
    """用户子图存储（Ego-Subgraph）"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # 中心用户
    c = Circle((4, 2.5), 0.4, facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1.2)
    ax.add_patch(c)
    ax.text(4, 2.5, 'User', ha='center', va='center', fontsize=10)

    # 物品/论文
    items = [(2, 4), (4, 4), (6, 4), (2, 1), (6, 1)]
    for ix, (px, py) in enumerate(items):
        c = Circle((px, py), 0.25, facecolor=ORANGE_FILL, edgecolor=ORANGE_EDGE, lw=1)
        ax.add_patch(c)
        ax.text(px, py, f'P{ix+1}', ha='center', va='center', fontsize=8)
        ax.plot([4, px], [2.5, py], color=TEXT_DARK, lw=1)

    ax.text(4, 0.5, 'Ego-Subgraph：以用户为中心的本地子图', ha='center', fontsize=10, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '用户子图示意图.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/用户子图示意图.png')


def fig_simulator_arch():
    """联邦学习仿真引擎架构"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    layers = [
        (5, 5, 'DataPartitioner\n(数据划分 / Non-IID)'),
        (5, 3.5, 'Client Simulator\n(多线程客户端)'),
        (5, 2, 'FedASCL Engine\n(FedASCL + 压缩)'),
        (5, 0.5, 'Aggregator\n(安全聚合)'),
    ]
    for cx, cy, t in layers:
        box = FancyBboxPatch((cx - 1.5, cy - 0.4), 3, 0.8, boxstyle="round,pad=0.02",
                             facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1.2)
        ax.add_patch(box)
        ax.text(cx, cy, t, ha='center', va='center', fontsize=9)
    for i in range(len(layers) - 1):
        _arrow(ax, 5, layers[i][1] - 0.4, 5, layers[i+1][1] + 0.4)

    ax.text(5, 5.6, '联邦学习仿真引擎架构', ha='center', fontsize=11, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '联邦学习仿真引擎架构图.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/联邦学习仿真引擎架构图.png')


def fig_coldstart_flow():
    """冷启动推荐策略流程：有交互->结构优先，无交互->属性映射"""
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font]
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # 决策菱形 -> 两个分支
    box0 = FancyBboxPatch((4, 2), 2, 1, boxstyle="round,pad=0.02",
                         facecolor=GRAY_BOX, edgecolor=TEXT_DARK, lw=1.2)
    ax.add_patch(box0)
    ax.text(5, 2.5, '用户有交互历史?', ha='center', va='center', fontsize=9)

    box1 = FancyBboxPatch((1.5, 3.8), 2, 0.8, boxstyle="round,pad=0.02",
                         facecolor=BLUE_FILL, edgecolor=BLUE_EDGE, lw=1)
    ax.add_patch(box1)
    ax.text(2.5, 4.2, '是: 结构优先', ha='center', va='center', fontsize=9)

    box2 = FancyBboxPatch((6.5, 3.8), 2, 0.8, boxstyle="round,pad=0.02",
                         facecolor=ORANGE_FILL, edgecolor=ORANGE_EDGE, lw=1)
    ax.add_patch(box2)
    ax.text(7.5, 4.2, '否: 属性映射', ha='center', va='center', fontsize=9)

    _arrow(ax, 4, 2.5, 2.5, 4)
    _arrow(ax, 6, 2.5, 7.5, 4)

    ax.text(5, 0.8, '冷启动推荐策略流程图', ha='center', fontsize=11, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '冷启动推荐策略流程图.png'), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print('Saved: images/冷启动推荐策略流程图.png')


def run_all():
    """运行所有概念图绘制"""
    fig_paper_structure()
    fig_bipartite_matrix()
    fig_gnn()
    fig_homo_hetero()
    fig_meta_path()
    fig_hypergraph_compare()
    fig_federated_learning()
    fig_horizontal_vertical_fl()
    fig_contrastive_learning()
    fig_fed_prototype_align()
    fig_attr_sem_graph()
    fig_cross_view_cl()
    fig_prototype_alignment()
    fig_compression_flow()
    fig_user_subgraph()
    fig_simulator_arch()
    fig_coldstart_flow()
    print('All conceptual figures done.')


if __name__ == '__main__':
    run_all()
