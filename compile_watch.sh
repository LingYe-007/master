#!/bin/bash
# 监听项目中的 .tex/.bib 等文件，修改后自动重新编译
# 使用: ./compile_watch.sh   （保持运行，保存文件即触发编译）

eval "$(/usr/libexec/path_helper 2>/dev/null)" || true

MAIN="main.tex"
OUT="output"
mkdir -p "$OUT"

echo "=========================================="
echo "已开启自动编译：修改并保存 .tex/.bib 等文件后将自动重新编译"
echo "按 Ctrl+C 停止"
echo "=========================================="
echo ""

latexmk -pdf -xelatex -outdir="$OUT" -interaction=nonstopmode -pvc "$MAIN"
