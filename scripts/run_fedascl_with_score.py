#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FedASCL 框架图绘制 + 自动评分 + 优化循环
- 先尝试下载素材包（可选）
- 绘制 -> 评分（SSIM vs model.png）-> 若得分>=90 停止，否则尝试下一组参数继续优化
依赖：pip install scikit-image
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUT_PATH = os.path.join(PROJECT_ROOT, 'images', 'fedascl_framework.png')
TARGET_SCORE = 90
MAX_ITER = 8


def main():
    sys.path.insert(0, SCRIPT_DIR)
    # 可选：下载素材
    try:
        from download_assets import download_assets
        download_assets()
    except Exception:
        pass

    from draw_fedascl_framework import draw_fedascl_framework
    from score_diagram import score_image

    ref = os.path.join(PROJECT_ROOT, 'images', 'model.png')
    if not os.path.isfile(ref):
        print(f'参考图不存在: {ref}，将仅绘制不评分')
        draw_fedascl_framework()
        return

    best_score = -1
    best_params = None

    # 多组参数用于优化
    param_sets = [
        {},
        {'dpi': 300, 'figscale': 1.0},
        {'dpi': 200, 'figscale': 1.05},
        {'dpi': 250, 'figscale': 0.98},
        {'dpi': 280, 'figscale': 1.02},
    ]

    for i, params in enumerate(param_sets):
        print(f'--- 第 {i+1}/{len(param_sets)} 次绘制 (params={params}) ---')
        draw_fedascl_framework(params)
        score, msg = score_image(OUT_PATH, ref)
        print(f'评分: {score}, {msg}')

        if score > best_score:
            best_score = score
            best_params = params

        if score >= TARGET_SCORE:
            print(f'达标！得分 {score} >= {TARGET_SCORE}，停止优化。')
            return

    print(f'经过 {len(param_sets)} 次尝试，最佳得分: {best_score} (params={best_params})')
    if best_score >= 0:
        print('未达 90 分，可手动优化或调整 score_diagram 评分逻辑。')


if __name__ == '__main__':
    main()
