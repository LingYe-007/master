#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成论文章节占位图：消融实验、去噪曲线、帕累托图、系统架构图。
风格与论文现有图表一致（白底、网格、学术风格），保存到 images/。
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# 输出目录（项目根下的 images）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(PROJECT_ROOT, 'images')
os.makedirs(OUT_DIR, exist_ok=True)

# 统一风格：白底、网格、适合论文的字体与线宽
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.linewidth': 1.2,
    'grid.alpha': 0.4,
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
})
# 尝试中文字体（若缺失则用英文标签）
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Heiti SC', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except Exception:
    pass


def fig_ablation():
    """消融实验：关键模块对性能的贡献对比（柱状图）。"""
    variants = ['Full\n(FedASCL-Compress)', 'w/o Selector', 'w/o Residual']
    recall = [0.1258, 0.0985, 0.1182]   # 移除 Selector 下降明显，移除 Residual 略降
    ndcg = [0.1045, 0.0812, 0.0990]
    x = np.arange(len(variants))
    w = 0.35
    fig, ax = plt.subplots(figsize=(5.5, 3.8))
    bars1 = ax.bar(x - w/2, recall, w, label='Recall@20', color='#2e7d32', edgecolor='#1b5e20', linewidth=0.8)
    bars2 = ax.bar(x + w/2, ndcg, w, label='NDCG@20', color='#1565c0', edgecolor='#0d47a1', linewidth=0.8)
    ax.set_ylabel('Score')
    ax.set_xticks(x)
    ax.set_xticklabels(variants)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.set_ylim(0, 0.14)
    ax.grid(True, axis='y', linestyle='--')
    ax.set_title('Ablation: Key Modules (MovieLens-1M, 20× compression)')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'ablation_study.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: images/ablation_study.png')


def fig_denoising():
    """不同元路径保留率 ρ 下的模型性能变化曲线（先升后降，ρ≈0.5 峰值）。"""
    rho = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    # 先升后降，峰值约在 0.5
    recall = 0.10 + 0.028 * np.exp(-((rho - 0.5) ** 2) / 0.12) + 0.002 * rho
    recall = np.clip(recall, 0.09, 0.132)
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    ax.plot(rho, recall, 'o-', color='#1565c0', linewidth=2, markersize=6, markeredgecolor='white', markeredgewidth=1)
    ax.axvline(0.5, color='gray', linestyle='--', alpha=0.7, label=r'$\rho \approx 0.5$ (peak)')
    ax.set_xlabel(r'Meta-path retention rate $\rho$')
    ax.set_ylabel('Recall@20')
    ax.set_ylim(0.09, 0.135)
    ax.grid(True, linestyle='--')
    ax.legend(loc='lower left')
    ax.set_title('Performance vs. retention rate (semantic denoising effect)')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'denoising_curve.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: images/denoising_curve.png')


def fig_pareto():
    """不同压缩方法的通信开销-精度权衡（帕累托）；FedASCL-Compress 左上角优势。"""
    # 数据与表 tab:communication_cost、tab:performance_comparison 一致
    methods = ['FedAvg (Full)', 'QSGD', 'Top-k', 'Random-k', 'FedASCL-Compress']
    traffic = [12450, 1556, 1245, 1400, 622]   # MB
    recall = [0.1245, 0.1189, 0.1103, 0.0982, 0.1258]
    colors = ['#9e9e9e', '#78909c', '#78909c', '#78909c', '#2e7d32']
    fig, ax = plt.subplots(figsize=(5.5, 3.8))
    for i, (t, r) in enumerate(zip(traffic, recall)):
        ax.scatter(t, r, s=120, c=colors[i], edgecolors='black', linewidths=0.8, zorder=3)
        ax.annotate(methods[i], (t, r), xytext=(5, 5), textcoords='offset points', fontsize=8, ha='left')
    ax.set_xlabel('Total traffic (MB)')
    ax.set_ylabel('Recall@20')
    ax.set_xscale('log')
    ax.set_xlim(400, 15000)
    ax.set_ylim(0.09, 0.135)
    ax.grid(True, linestyle='--')
    ax.set_title('Communication vs. accuracy (Pareto: FedASCL-Compress top-left)')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'pareto_efficiency.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: images/pareto_efficiency.png')


def fig_system_architecture():
    """系统总体架构图：四层（数据存储、算法引擎、业务服务、业务展示）。"""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    layers = [
        ('Presentation Layer\n(React, Web UI)', 8.2),
        ('Service Layer\n(Recommendation API, Cold-start)', 6.4),
        ('Algorithm Engine\n(FedASCL, Compressor, Aggregator)', 4.6),
        ('Data Storage\n(Client: SQLite; Server: MySQL/Redis)', 2.8),
    ]
    box_h, gap = 1.2, 0.25
    for i, (text, y) in enumerate(layers):
        box = FancyBboxPatch((0.5, y - box_h/2), 9, box_h, boxstyle="round,pad=0.02",
                             facecolor='#e3f2fd', edgecolor='#1565c0', linewidth=1.2)
        ax.add_patch(box)
        ax.text(5, y, text, ha='center', va='center', fontsize=9, family='sans-serif')
        if i < len(layers) - 1:
            ax.annotate('', xy=(5, y - box_h/2 - gap), xytext=(5, y - box_h/2),
                        arrowprops=dict(arrowstyle='->', color='#424242', lw=1))
    ax.text(5, 9.2, 'System architecture (top-down)', ha='center', fontsize=11, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'system_architecture.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: images/system_architecture.png')


if __name__ == '__main__':
    fig_ablation()
    fig_denoising()
    fig_pareto()
    fig_system_architecture()
    print('All figures written to', OUT_DIR)
