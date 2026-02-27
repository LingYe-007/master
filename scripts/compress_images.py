# -*- coding: utf-8 -*-
"""
压缩 images/ 目录下图片，使论文 PDF 体积减小（目标：PDF < 30MB）。
- 将过大的图片（长边 > 1600px 或 文件 > 800KB）缩放到长边 1600px，并适当压缩。
- 原图会备份到 images/backup/，如需恢复可从该目录复制回来。
运行：在项目根目录执行  python scripts/compress_images.py
依赖：pip install Pillow
"""

import os
import shutil
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("请先安装 Pillow: pip install Pillow")
    exit(1)

# 项目根目录与 images 目录
ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "images"
BACKUP_DIR = IMAGES_DIR / "backup"

# 仅处理这些扩展名
EXTS = {".png", ".jpg", ".jpeg", ".webp"}
# 长边超过此值则缩放
MAX_SIDE = 1600
# 文件大于此值（字节）则尝试压缩
MIN_SIZE_TO_SHRINK = 800 * 1024  # 800KB
# JPG 质量（用于另存为 JPG 时）
JPG_QUALITY = 88


def backup(path: Path) -> None:
    """备份原图到 images/backup/"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    dest = BACKUP_DIR / path.name
    if not dest.exists() or dest.stat().st_size != path.stat().st_size:
        shutil.copy2(path, dest)
        print(f"  已备份: {path.name}")


def compress_image(path: Path) -> bool:
    """压缩单张图片：若过大则缩放并覆盖。返回是否已修改。"""
    if path.suffix.lower() not in EXTS:
        return False
    size_kb = path.stat().st_size / 1024
    try:
        img = Image.open(path)
    except Exception as e:
        print(f"  跳过（无法打开）: {path.name} - {e}")
        return False
    if img.mode in ("RGBA", "P"):
        # PNG 带透明通道，保持 PNG
        need_resize = max(img.size) > MAX_SIDE or path.stat().st_size > MIN_SIZE_TO_SHRINK
        if not need_resize:
            return False
        backup(path)
        if max(img.size) > MAX_SIDE:
            ratio = MAX_SIDE / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        img.save(path, "PNG", optimize=True)
        new_kb = path.stat().st_size / 1024
        print(f"  已压缩 PNG: {path.name}  {size_kb:.0f} KB -> {new_kb:.0f} KB")
        return True
    # 非透明图可存为 JPG 以减小体积
    need_resize = max(img.size) > MAX_SIDE or path.stat().st_size > MIN_SIZE_TO_SHRINK
    if not need_resize:
        return False
    backup(path)
    if max(img.size) > MAX_SIDE:
        ratio = MAX_SIDE / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    if img.mode != "RGB":
        img = img.convert("RGB")
    # 大图优先改为 jpg 以显著减小体积（需注意：扩展名改变后 tex 里要改引用）
    # 为保险起见，不改扩展名，仅缩小尺寸并覆盖原 PNG/JPG
    if path.suffix.lower() in {".png", ".webp"}:
        # 若原为 png，保存为 png 但压缩
        img.save(path, "PNG", optimize=True)
    else:
        img.save(path, "JPEG", quality=JPG_QUALITY, optimize=True)
    new_kb = path.stat().st_size / 1024
    print(f"  已压缩: {path.name}  {size_kb:.0f} KB -> {new_kb:.0f} KB")
    return True


def main():
    os.chdir(ROOT)
    if not IMAGES_DIR.exists():
        print("未找到 images 目录")
        return
    print("正在压缩 images/ 下过大图片（长边 > %dpx 或 文件 > %.0fKB）..." % (MAX_SIDE, MIN_SIZE_TO_SHRINK / 1024))
    count = 0
    for f in sorted(IMAGES_DIR.iterdir()):
        if f.is_file() and f.suffix.lower() in EXTS and f.name != "option.tex":
            if compress_image(f):
                count += 1
    print("处理完成，共压缩 %d 张。请重新编译论文生成 PDF。" % count)
    if count > 0:
        print("原图已备份至 images/backup/ ，如需恢复可从中复制回来。")


if __name__ == "__main__":
    main()
