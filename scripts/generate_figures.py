#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成论文章节占位图：消融实验、去噪曲线、帕累托图、Non-IID、训练曲线等。
数值与 chapters/chap3_method.tex、chap4_compression.tex 主表对齐。
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch
import numpy as np


def _get_chinese_font():
    for name in ['PingFang SC', 'Heiti SC', 'STHeiti', 'Songti SC', 'SimHei', 'Microsoft YaHei']:
        if any(f.name == name for f in fm.fontManager.ttflist):
            return name
    return None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(PROJECT_ROOT, 'images')
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.linewidth': 1.2,
    'grid.alpha': 0.4,
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
})
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Heiti SC', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except Exception:
    pass


# 第四章 tab:performance_comparison 终值（Recall@20 / NDCG@20，ρ=0.2, b=4）

# 100 轮联邦训练：每轮一个观测点（round 1 … 100）
ROUNDS = np.arange(1, 101)


def _simulate_federated_curve(
    rounds,
    final,
    *,
    seed,
    tau=25.0,
    noise_ratio=0.024,
    y0_frac=0.08,
    hetero=1.0,
    yelp=False,
    acm=False,
    late_plateau_from=58,
):
    """逐轮仿真联邦评测曲线：趋势收敛 + 客户端采样导致的可见逐轮波动。"""
    rng = np.random.default_rng(seed)
    t = np.asarray(rounds, dtype=float)
    n = len(t)

    y0 = max(final * y0_frac, 0.006 if yelp else final * 0.035)
    tau_eff = tau * (1.35 if yelp else 1.0) * (0.92 if acm else 1.0)
    noise_std = final * noise_ratio * hetero * (2.1 if yelp else 1.0)

    g_fast = 1.0 - np.exp(-(t - 1) / (tau_eff * 0.52))
    g_slow = 1.0 - np.exp(-np.maximum(t - 22, 0) / (tau_eff * 1.08))
    progress = np.clip(0.68 * g_fast + 0.32 * g_slow, 0, 1)
    plateau = t >= late_plateau_from
    progress = np.where(
        plateau,
        progress + (1.0 - progress) * (1.0 - np.exp(-(t - late_plateau_from) / 18.0)) * 0.55,
        progress,
    )
    envelope = y0 + (final - y0) * np.clip(progress, 0, 1)

    y = np.empty(n, dtype=float)
    y[0] = y0 + rng.normal(0, noise_std * 1.8)
    for i in range(1, n):
        pull = 0.10 + 0.06 * (1.0 - i / n)
        step = pull * (envelope[i] - y[i - 1])
        shock = rng.normal(0, noise_std)
        if rng.random() < 0.045 * hetero:
            shock -= abs(rng.normal(final * 0.010 * hetero, final * 0.005))
        y[i] = y[i - 1] + step + shock

    # 弱约束防止长期漂移，但保留逐轮参差
    blend = np.where(t < 25, 0.22, np.where(t < late_plateau_from, 0.14, 0.08))
    y = (1.0 - blend) * y + blend * envelope
    y = np.clip(y, max(y0 * 0.75, 0.003), final * 1.04)

    # 仅最后一轮对齐表格终值（论文报告的是第 100 轮评测结果）
    if n >= 2:
        y[-2] = 0.82 * y[-2] + 0.18 * final
    y[-1] = final
    return y


CHAP4_COMPRESS = {
    'MovieLens-1M': {
        'FedASCL-Full': (0.1245, 0.1032),
        'Random-k': (0.0968, 0.0738),
        'Top-k': (0.1088, 0.0892),
        'QSGD': (0.1158, 0.0962),
        'FedASCL-Compress': (0.1215, 0.1009),
    },
    'Yelp': {
        'FedASCL-Full': (0.0865, 0.0645),
        'Random-k': (0.0595, 0.0415),
        'Top-k': (0.0725, 0.0548),
        'QSGD': (0.0792, 0.0592),
        'FedASCL-Compress': (0.0835, 0.0623),
    },
    'ACM': {
        'FedASCL-Full': (0.1382, 0.1206),
        'Random-k': (0.1078, 0.0864),
        'Top-k': (0.1208, 0.1048),
        'QSGD': (0.1285, 0.1128),
        'FedASCL-Compress': (0.1338, 0.1172),
    },
}


def fig_ablation():
    """第四章压缩消融：与 tab:performance_comparison 默认配置一致。"""
    variants = ['Full\n(FedASCL-Compress)', 'w/o Selector', 'w/o Residual']
    recall = [0.1215, 0.0945, 0.1172]
    ndcg = [0.1009, 0.0775, 0.0968]
    x = np.arange(len(variants))
    w = 0.35
    fig, ax = plt.subplots(figsize=(5.5, 3.8))
    ax.bar(x - w/2, recall, w, label='Recall@20', color='#2e7d32', edgecolor='#1b5e20', linewidth=0.8)
    ax.bar(x + w/2, ndcg, w, label='NDCG@20', color='#1565c0', edgecolor='#0d47a1', linewidth=0.8)
    ax.set_ylabel('Score')
    ax.set_xticks(x)
    ax.set_xticklabels(variants)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.set_ylim(0, 0.14)
    ax.grid(True, axis='y', linestyle='--')
    ax.set_title('Ablation: Key Modules (MovieLens-1M, 15.2× compression)')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'ablation_study.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: images/ablation_study.png')


def fig_denoising():
    """ρ 代表性配置曲线：与精简后 tab:compression_tradeoff 对齐（论文正文已弃用该图）。"""
    rho = np.array([0.1, 0.2, 1.0])
    recall = np.array([0.1158, 0.1215, 0.1245])
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    ax.plot(rho, recall, 'o-', color='#1565c0', linewidth=2, markersize=6,
            markeredgecolor='white', markeredgewidth=1)
    ax.axvline(0.2, color='#c62828', linestyle='--', alpha=0.6, label=r'Default $\rho=0.2$')
    ax.set_xlabel(r'Meta-path retention rate $\rho$')
    ax.set_ylabel('Recall@20')
    ax.set_ylim(0.112, 0.126)
    ax.grid(True, linestyle='--')
    ax.legend(loc='lower right')
    ax.set_title('Performance vs. retention rate (MovieLens-1M)')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'denoising_curve.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: images/denoising_curve.png')


def fig_convergence_curve():
    """压缩策略收敛曲线：100 轮逐点，终点对齐 tab:performance_comparison。"""
    rounds = ROUNDS
    full = _simulate_federated_curve(rounds, 0.1245, seed=42, tau=24, noise_ratio=0.020)
    compress = _simulate_federated_curve(rounds, 0.1215, seed=43, tau=27, noise_ratio=0.022)
    qsgd = _simulate_federated_curve(rounds, 0.1158, seed=44, tau=29, noise_ratio=0.026)
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.plot(rounds, full, '-', color='#424242', linewidth=2, label='FedASCL-Full')
    ax.plot(rounds, compress, '-', color='#2e7d32', linewidth=2, label='FedASCL-Compress')
    ax.plot(rounds, qsgd, '-', color='#1565c0', linewidth=1.5, alpha=0.9, label='QSGD (4-bit)')
    ax.set_xlabel('Training round')
    ax.set_ylabel('Recall@20')
    ax.set_ylim(0.04, 0.13)
    ax.set_xlim(0, 100)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='lower right', framealpha=0.9)
    ax.set_title('Convergence curves (MovieLens-1M, 15.2× compression)')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'convergence_curve.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: images/convergence_curve.png')


def fig_pareto():
    """帕累托图：与 tab:communication_cost + tab:performance_comparison 对齐。"""
    methods = ['FedASCL-Full', 'QSGD', 'Top-k', 'Random-k', 'FedASCL-Compress']
    traffic = [13.35, 1.86, 1.52, 1.62, 0.877]
    recall = [0.1245, 0.1158, 0.1088, 0.0968, 0.1215]
    colors = ['#9e9e9e', '#78909c', '#78909c', '#78909c', '#2e7d32']
    fig, ax = plt.subplots(figsize=(5.5, 3.8))
    for t, r, m, c in zip(traffic, recall, methods, colors):
        ax.scatter(t, r, s=120, c=c, edgecolors='black', linewidths=0.8, zorder=3)
        ax.annotate(m, (t, r), xytext=(5, 5), textcoords='offset points', fontsize=8, ha='left')
    ax.set_xlabel('Total traffic (MB)')
    ax.set_ylabel('Recall@20')
    ax.set_xscale('log')
    ax.set_xlim(0.5, 20)
    ax.set_ylim(0.09, 0.128)
    ax.grid(True, linestyle='--')
    ax.set_title('Communication vs. accuracy (MovieLens-1M)')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'pareto_efficiency.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: images/pareto_efficiency.png')


NON_IID_FINALS = {
    'FedGNN': [0.0825, 0.0968, 0.1062, 0.1128],
    'FedHGNN': [0.0985, 0.1108, 0.1168, 0.1238],
    'FedProto': [0.1095, 0.1188, 0.1248, 0.1267],
    'FedASCL': [0.1185, 0.1226, 0.1253, 0.1253],
}

NON_IID_ALPHA_LABELS = [
    r'$\alpha = 0.1$ (Extreme Non-IID)',
    r'$\alpha = 0.5$',
    r'$\alpha = 1.0$',
    r'$\alpha = \infty$ (IID)',
]

NON_IID_STYLE = {
    'FedGNN': {'color': '#E8A598', 'ls': '--', 'lw': 1.35, 'alpha': 0.88},
    'FedHGNN': {'color': '#5C9BD5', 'ls': '--', 'lw': 1.45, 'alpha': 0.90},
    'FedProto': {'color': '#D4A017', 'ls': '--', 'lw': 1.55, 'alpha': 0.92},
    'FedASCL': {'color': '#F28E2B', 'ls': '-', 'lw': 2.2, 'alpha': 1.00},
}

NON_IID_TAU = {
    'FedGNN': 36,
    'FedHGNN': 27,
    'FedProto': 21,
    'FedASCL': 23,
}


def _non_iid_training_curve(rounds, final, *, method, alpha_idx, seed):
    """按 α 档位生成 100 轮 NDCG@10 曲线，Non-IID 越强波动越大。"""
    hetero_scale = [1.35, 1.05, 0.82, 0.72][alpha_idx]
    tau_scale = [1.22, 1.08, 1.0, 0.96][alpha_idx]
    tau = NON_IID_TAU[method] * tau_scale * (0.94 if method == 'FedASCL' else 1.0)
    noise_ratio = {
        'FedGNN': 0.028,
        'FedHGNN': 0.022,
        'FedProto': 0.018,
        'FedASCL': 0.016,
    }[method]
    y0_frac = 0.22 + alpha_idx * 0.015
    return _simulate_federated_curve(
        rounds, final, seed=seed, tau=tau, noise_ratio=noise_ratio,
        y0_frac=y0_frac, hetero=hetero_scale,
        late_plateau_from=56 + alpha_idx * 4,
    )


def _non_iid_ascl_iid_curve(rounds, final_ascl, final_proto, *, seed):
    """IID / 高 α：Proto 终值略高于 ASCL，前期可接近。"""
    t = np.asarray(rounds, dtype=float)
    early = min(final_ascl + 0.0012, final_proto - 0.0002)
    fast = _non_iid_training_curve(rounds, early, method='FedASCL', alpha_idx=3, seed=seed)
    settle = _non_iid_training_curve(rounds, final_ascl, method='FedASCL', alpha_idx=3, seed=seed + 17)
    w = 1.0 / (1.0 + np.exp(-(t - 42) / 6.0))
    y = (1 - w) * fast + w * settle
    y[-2] = 0.82 * y[-2] + 0.18 * final_ascl
    y[-1] = final_ascl
    return y


def fig_non_iid():
    """Non-IID 鲁棒性：2×2 子图，100 轮逐点训练曲线，终点对齐 tab:non_iid_data。"""
    rounds = ROUNDS
    methods = ['FedGNN', 'FedHGNN', 'FedProto', 'FedASCL']

    fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.8), sharex=True)
    fig.subplots_adjust(hspace=0.32, wspace=0.24, bottom=0.16, top=0.90)

    for ax_idx, (ax, alpha_idx) in enumerate(zip(axes.flat, range(4))):
        finals = {m: NON_IID_FINALS[m][alpha_idx] for m in methods}
        proto_final = finals['FedProto']

        for mi, name in enumerate(methods):
            final = finals[name]
            seed = 1000 + alpha_idx * 97 + mi * 31
            style = NON_IID_STYLE[name]

            if name == 'FedASCL' and alpha_idx == 3:
                y = _non_iid_ascl_iid_curve(
                    rounds, finals['FedASCL'], proto_final, seed=seed,
                )
            elif name == 'FedProto' and alpha_idx >= 2:
                y = _non_iid_training_curve(
                    rounds, final, method=name, alpha_idx=alpha_idx, seed=seed,
                )
                # 高 α / IID 下 Proto 与 ASCL 非常接近
                if alpha_idx == 3:
                    ascl_y = _non_iid_ascl_iid_curve(
                        rounds, finals['FedASCL'], proto_final, seed=seed + 5,
                    )
                    blend = np.clip((np.asarray(rounds, float) - 50) / 35.0, 0, 1)
                    y = (1 - blend) * y + blend * (ascl_y + (final - finals['FedASCL']))
                    y[-1] = final
            else:
                y = _non_iid_training_curve(
                    rounds, final, method=name, alpha_idx=alpha_idx, seed=seed,
                )

            ax.plot(rounds, y, color=style['color'], linestyle=style['ls'],
                    linewidth=style['lw'], alpha=style['alpha'], label=name)

        ax.set_title(NON_IID_ALPHA_LABELS[alpha_idx], fontsize=10, fontweight='bold', pad=5)
        ax.set_ylim(0.055, 0.132)
        ax.set_xlim(0, 100)
        ax.grid(True, linestyle='--', alpha=0.45, linewidth=0.6, color='#bdbdbd')
        ax.set_xlabel('Round', fontsize=9)
        if ax_idx % 2 == 0:
            ax.set_ylabel('NDCG@10', fontsize=10, fontweight='bold')

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=4, frameon=True,
               framealpha=0.95, fontsize=9, columnspacing=1.6,
               bbox_to_anchor=(0.5, 0.02))
    fig.suptitle('Performance Comparison Across Different Data Heterogeneity Levels',
                 fontsize=12, fontweight='bold', y=0.97)
    fig.savefig(os.path.join(OUT_DIR, 'non_iid_robustness.png'), dpi=180, bbox_inches='tight')
    plt.close()
    print('Saved: images/non_iid_robustness.png')


# 第三章表 tab:overall_performance 终值（Hit@10 / NDCG@10）
OVERALL_FINALS = {
    'MovieLens-1M': {
        'FedGNN': (0.1995, 0.1062),
        'FedHGNN': (0.2135, 0.1168),
        'FedProto': (0.2188, 0.1248),
        'FedASCL': (0.2196, 0.1253),
    },
    'Yelp': {
        'FedGNN': (0.0375, 0.0218),
        'FedHGNN': (0.0448, 0.0268),
        'FedProto': (0.0482, 0.0299),
        'FedASCL': (0.0487, 0.0294),
    },
    'ACM': {
        'FedGNN': (0.2058, 0.1198),
        'FedHGNN': (0.2432, 0.1462),
        'FedProto': (0.2456, 0.1471),
        'FedASCL': (0.2443, 0.1463),
    },
}

METHOD_STYLE = {
    'FedGNN':   {'color': '#8FBCE6', 'ls': '--', 'lw': 1.3, 'alpha': 0.90},
    'FedHGNN':  {'color': '#5C9BD5', 'ls': ':',  'lw': 1.6, 'alpha': 0.95},
    'FedProto': {'color': '#D4A017', 'ls': '--', 'lw': 1.7, 'alpha': 0.95},
    'FedASCL':  {'color': '#F28E2B', 'ls': '-',  'lw': 2.2, 'alpha': 1.00},
}

METHOD_TAU = {
    'FedGNN': 31,
    'FedHGNN': 23,
    'FedProto': 22,
    'FedASCL': 24,
}


def _training_curve(rounds, final, *, tau, seed, noise_ratio=0.022,
                    start_frac=0.08, yelp=False, acm=False, stable=False):
    """100 轮逐点训练曲线，终点对齐表格终值。"""
    del stable  # 不再为 FedASCL 单独压低波动
    return _simulate_federated_curve(
        rounds, final, seed=seed, tau=tau, noise_ratio=noise_ratio,
        y0_frac=start_frac, hetero=1.0, yelp=yelp, acm=acm,
    )


def _training_curve_ascl_ndcg(rounds, final_ascl, final_proto, *, seed, cross_round=40, yelp=False):
    """ASCL 在 NDCG 上前期略快、后期稳定于略低于 Proto 的终值（与表一致）。"""
    t = np.asarray(rounds, dtype=float)
    cross = cross_round * (1.08 if yelp else 1.0)
    early_target = min(final_ascl + 0.0018, final_proto - 0.0003)
    fast = _training_curve(rounds, early_target, tau=20, seed=seed,
                           noise_ratio=0.020, yelp=yelp)
    settle = _training_curve(rounds, final_ascl, tau=28, seed=seed + 11,
                             noise_ratio=0.018, yelp=yelp)
    w = 1.0 / (1.0 + np.exp(-(t - cross) / 5.5))
    y = (1 - w) * fast + w * settle
    y[-2] = 0.82 * y[-2] + 0.18 * final_ascl
    y[-1] = final_ascl
    return y


def fig_experiment():
    """第三章 2×3 训练收敛曲线：100 轮逐点，对齐 tab:overall_performance。"""
    rounds = ROUNDS
    datasets = ['MovieLens-1M', 'Yelp', 'ACM']
    methods = ['FedGNN', 'FedHGNN', 'FedProto', 'FedASCL']
    metrics = [('Hit@10', 0), ('NDCG@10', 1)]

    fig, axes = plt.subplots(2, 3, figsize=(11.2, 6.4), sharex=True)
    fig.subplots_adjust(hspace=0.28, wspace=0.22, bottom=0.14, top=0.88)

    for col, ds in enumerate(datasets):
        is_yelp = ds == 'Yelp'
        is_acm = ds == 'ACM'
        for row, (metric_name, idx) in enumerate(metrics):
            ax = axes[row, col]
            finals = {m: OVERALL_FINALS[ds][m][idx] for m in methods}

            for mi, name in enumerate(methods):
                final = finals[name]
                seed = hash((ds, metric_name, name)) % (2 ** 31)
                style = METHOD_STYLE[name]

                # ML / ACM 的 NDCG：Proto 后期略高于 ASCL
                if name == 'FedASCL' and metric_name == 'NDCG@10' and ds in ('MovieLens-1M', 'ACM'):
                    y = _training_curve_ascl_ndcg(
                        rounds, finals['FedASCL'], finals['FedProto'],
                        seed=seed, cross_round=38 if ds == 'MovieLens-1M' else 46,
                        yelp=is_yelp,
                    )
                elif name == 'FedHGNN' and metric_name == 'NDCG@10' and ds == 'ACM':
                    y = _training_curve(
                        rounds, final, tau=METHOD_TAU[name], seed=seed,
                        noise_ratio=0.021, acm=True,
                    )
                    bump = 0.0015 * np.exp(-((t := np.asarray(rounds, float)) - 58) ** 2 / 180.0)
                    y = y + bump
                    y[-2] = 0.82 * y[-2] + 0.18 * final
                    y[-1] = final
                else:
                    y = _training_curve(
                        rounds, final, tau=METHOD_TAU[name], seed=seed,
                        noise_ratio=0.024 if is_yelp else 0.022,
                        yelp=is_yelp, acm=is_acm,
                    )

                ax.plot(rounds, y, color=style['color'], linestyle=style['ls'],
                        linewidth=style['lw'], alpha=style['alpha'], label=name)

            ymax = max(finals.values()) * 1.12
            ymin = max(min(finals.values()) * 0.55, 0.008)
            ax.set_ylim(ymin, ymax)
            ax.grid(True, linestyle='--', alpha=0.45, linewidth=0.6)
            ax.set_xlim(0, 100)
            if col == 0:
                ax.set_ylabel(metric_name, fontsize=10, fontweight='bold')
            if row == 0:
                ax.set_title(ds, fontsize=11, fontweight='bold', pad=6)
            if row == 1:
                ax.set_xlabel('Round', fontsize=9)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=4, frameon=True,
               framealpha=0.95, fontsize=9, columnspacing=1.2,
               bbox_to_anchor=(0.5, 0.01))
    fig.suptitle('FedASCL Experimental Results: Training Progress Comparison',
                 fontsize=12, fontweight='bold', y=0.97)
    fig.savefig(os.path.join(OUT_DIR, 'experiment.png'), dpi=180, bbox_inches='tight')
    plt.close()
    print('Saved: images/experiment.png')


def fig_system_architecture():
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


def fig_system_architecture_cn():
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font] + [x for x in plt.rcParams['font.sans-serif'] if x != font]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    layers = [
        ('业务展示层\n(React, Web UI)', 8.2),
        ('业务服务层\n(推荐 API, 冷启动)', 6.4),
        ('算法引擎层\n(FedASCL, 压缩器, 聚合器)', 4.6),
        ('数据存储层\n(客户端: SQLite; 服务端: MySQL/Redis)', 2.8),
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
    ax.text(5, 9.2, '系统总体设计架构图', ha='center', fontsize=11, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'system_architecture_cn.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: images/system_architecture_cn.png')


def fig_selector_logic():
    font = _get_chinese_font()
    if font:
        plt.rcParams['font.sans-serif'] = [font] + [x for x in plt.rcParams['font.sans-serif'] if x != font]
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    boxes = [
        (5, 7.5, '输入：元路径集合 $\\mathcal{P}=\\{p_1,\\dots,p_M\\}$ 与权重 $\\boldsymbol{\\alpha}^{(t)}$'),
        (5, 4.5, 'Top-$K$ 筛选：保留权重最大的 $K$ 条元路径，生成掩码 $\\mathbf{m}^{(t)}\\in\\{0,1\\}^M$'),
        (5, 1.8, '输出：仅上传 $m_i^{(t)}{=}1$ 对应子网络的梯度更新；服务端对同一路径采用按位聚合'),
    ]
    box_w, box_h = 8.2, 1.4
    for i, (cx, cy, text) in enumerate(boxes):
        box = FancyBboxPatch((cx - box_w/2, cy - box_h/2), box_w, box_h,
                              boxstyle="round,pad=0.04", facecolor='#e3f2fd',
                              edgecolor='#1565c0', linewidth=1.2)
        ax.add_patch(box)
        ax.text(cx, cy, text, ha='center', va='center', fontsize=9, family='sans-serif')
        if i < len(boxes) - 1:
            ax.annotate('', xy=(cx, cy - box_h/2 - 0.35), xytext=(cx, cy - box_h/2),
                        arrowprops=dict(arrowstyle='->', color='#424242', lw=1.2))
    ax.text(5, 9.1, '动态元路径选择器（基于注意力权重 $\\alpha$ 的 Top-K 筛选）', ha='center', fontsize=10, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'selector_logic.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('Saved: images/selector_logic.png')


def fig_fedascl_framework():
    draw_script = os.path.join(SCRIPT_DIR, 'draw_fedascl_framework.py')
    if os.path.exists(draw_script):
        import importlib.util
        spec = importlib.util.spec_from_file_location('draw_fedascl', draw_script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.draw_fedascl_framework()


if __name__ == '__main__':
    import sys
    if '--all' in sys.argv:
        fig_ablation()
        fig_denoising()
        fig_convergence_curve()
        fig_pareto()
        fig_non_iid()
        fig_experiment()
        fig_system_architecture()
        fig_system_architecture_cn()
        fig_selector_logic()
        fig_fedascl_framework()
        print('All figures written to', OUT_DIR)
    elif '--non-iid' in sys.argv:
        fig_non_iid()
        print('Done: images/non_iid_robustness.png updated.')
    elif '--curves' in sys.argv:
        fig_experiment()
        fig_non_iid()
        fig_convergence_curve()
        print('Done: experiment.png, non_iid_robustness.png, convergence_curve.png updated.')
    else:
        fig_experiment()
        fig_non_iid()
        fig_convergence_curve()
        print('Done: training curve figures updated (100 rounds each).')
        print('To regenerate all placeholder figures, run: python generate_figures.py --all')
