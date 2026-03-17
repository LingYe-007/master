#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FedASCL 框架图质量评分：与 model.png 对比 SSIM，返回 0-100 分
依赖：pip install scikit-image
"""
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
REF_PATH = os.path.join(PROJECT_ROOT, 'images', 'model.png')


def score_image(output_path, ref_path=None):
    """
    评分：SSIM 结构相似度 * 100，与参考图 model.png 对比。
    若参考图不存在或无 scikit-image，返回 -1。
    """
    ref_path = ref_path or REF_PATH
    if not os.path.isfile(ref_path):
        return -1, "参考图不存在: " + ref_path
    if not os.path.isfile(output_path):
        return -1, "输出图不存在: " + output_path

    try:
        from skimage.metrics import structural_similarity as ssim
        from skimage import io
        from skimage.transform import resize
        import numpy as np
    except ImportError:
        return -1, "请安装 scikit-image: pip install scikit-image"

    try:
        img_out = io.imread(output_path)
        img_ref = io.imread(ref_path)

        # RGBA -> RGB（取前3通道）
        if img_out.ndim == 3 and img_out.shape[-1] == 4:
            img_out = img_out[:, :, :3]
        if img_ref.ndim == 3 and img_ref.shape[-1] == 4:
            img_ref = img_ref[:, :, :3]

        # 统一为灰度、统一尺寸
        if img_out.ndim == 3:
            from skimage.color import rgb2gray
            img_out = rgb2gray(img_out)
        if img_ref.ndim == 3:
            from skimage.color import rgb2gray
            img_ref = rgb2gray(img_ref)

        h, w = 400, 560  # 固定比较尺寸
        img_out = resize(img_out, (h, w), anti_aliasing=True, preserve_range=True)
        img_ref = resize(img_ref, (h, w), anti_aliasing=True, preserve_range=True)

        data_range = max(img_out.max() - img_out.min(), img_ref.max() - img_ref.min(), 1.0)
        score_01 = ssim(img_out, img_ref, data_range=data_range)
        score_100 = min(100, max(0, score_01 * 100))
        return round(score_100, 1), f"SSIM={score_01:.3f} -> {score_100:.1f}分"
    except Exception as e:
        return -1, str(e)


if __name__ == '__main__':
    out = os.path.join(PROJECT_ROOT, 'images', 'fedascl_framework.png')
    s, msg = score_image(out)
    print(f"评分: {s}, {msg}")
