#!/bin/bash
# 使用方法: ./make_icns.sh appicon.png
# 传入一张 1024x1024 的 PNG 图片，就能生成 appicon.icns

INPUT_FILE="$1"
if [ -z "$INPUT_FILE" ]; then
  echo "❌ 请提供 PNG 文件，比如: ./make_icns.sh appicon.png"
  exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
  echo "❌ 文件不存在: $INPUT_FILE"
  exit 1
fi

# 创建临时文件夹
ICONSET="AppIcon.iconset"
mkdir -p "$ICONSET"

# 生成多尺寸图标
sips -z 16 16     "$INPUT_FILE" --out "$ICONSET/icon_16x16.png"
sips -z 32 32     "$INPUT_FILE" --out "$ICONSET/icon_16x16@2x.png"
sips -z 32 32     "$INPUT_FILE" --out "$ICONSET/icon_32x32.png"
sips -z 64 64     "$INPUT_FILE" --out "$ICONSET/icon_32x32@2x.png"
sips -z 128 128   "$INPUT_FILE" --out "$ICONSET/icon_128x128.png"
sips -z 256 256   "$INPUT_FILE" --out "$ICONSET/icon_128x128@2x.png"
sips -z 256 256   "$INPUT_FILE" --out "$ICONSET/icon_256x256.png"
sips -z 512 512   "$INPUT_FILE" --out "$ICONSET/icon_256x256@2x.png"
sips -z 512 512   "$INPUT_FILE" --out "$ICONSET/icon_512x512.png"
cp "$INPUT_FILE" "$ICONSET/icon_512x512@2x.png"

# 生成 icns
iconutil -c icns "$ICONSET" -o appicon.icns

echo "✅ 已生成 appicon.icns"