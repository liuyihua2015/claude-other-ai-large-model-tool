#!/usr/bin/env python3
from PIL import Image
import os
import sys


def icns_to_png(icns_path, png_path="icon_temp.png"):
    """将 .icns 文件提取为 PNG"""
    try:
        img = Image.open(icns_path)
        img.save(png_path)
        print(f"✅ ICNS 转 PNG 成功: {png_path}")
        return png_path
    except Exception as e:
        print(f"❌ ICNS 转 PNG 失败: {e}")
        sys.exit(1)


def generate_ico(input_image, output_ico="icon.ico"):
    """生成多尺寸 Windows 图标"""
    try:
        img = Image.open(input_image)
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(output_ico, format="ICO", sizes=sizes)
        print(f"✅ ICO 文件生成成功: {output_ico}")
    except Exception as e:
        print(f"❌ ICO 文件生成失败: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("用法: python generate_icon.py <input.png 或 .icns> [输出.ico]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_ico = sys.argv[2] if len(sys.argv) > 2 else "icon.ico"

    # 如果是 icns 文件，先转 png
    if input_file.lower().endswith(".icns"):
        png_file = icns_to_png(input_file)
    else:
        png_file = input_file

    generate_ico(png_file, output_ico)

    # 如果生成的是临时 PNG，删除
    if input_file.lower().endswith(".icns") and os.path.exists(png_file):
        os.remove(png_file)


if __name__ == "__main__":
    main()
