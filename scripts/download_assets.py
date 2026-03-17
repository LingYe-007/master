#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载 FedASCL 框架图素材包（云、齿轮、图结构等图标）
若下载失败则使用程序绘制，不影响主流程
"""
import os
import urllib.request
import ssl

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, 'assets', 'icons')
os.makedirs(ASSETS_DIR, exist_ok=True)


def _download(url, out_path):
    """下载文件，忽略证书验证"""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            with open(out_path, 'wb') as f:
                f.write(r.read())
        return True
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return False


def download_assets():
    """尝试下载图标素材（可选，失败则沿用程序绘制）"""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    icons = []  # 可添加实际素材 URL，例: ('cloud','https://...')
    ok = 0
    for name, url in icons:
        out = os.path.join(ASSETS_DIR, f'{name}.svg')
        if _download(url, out):
            ok += 1
            print(f'已下载: {out}')
    print(f'素材下载完成: {ok}/{len(icons)}')
    return ok


if __name__ == '__main__':
    download_assets()
