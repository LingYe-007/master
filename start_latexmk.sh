#!/bin/bash
# 启动 latexmk 持续预览模式（单进程版本）

eval "$(/usr/libexec/path_helper)"

MAIN="main.tex"
OUT="output"

# 检查并停止已存在的进程
if pgrep -f "latexmk.*$MAIN" > /dev/null; then
    echo "发现已有 latexmk 进程，正在停止..."
    pkill -f "latexmk.*$MAIN"
    sleep 1
fi

echo "=== 启动 LaTeXmk 持续预览模式 ==="
echo "监听文件变化，自动编译..."
echo "按 Ctrl+C 停止"
echo ""

# 创建输出目录
mkdir -p "$OUT"

# 启动 latexmk 持续预览模式（单进程，后台运行）
# 使用 -pvc 持续预览模式，即使有错误也继续监听文件变化
# 注意：不使用 -view=pdf，让 Cursor 的内部查看器处理 PDF 打开
nohup latexmk -pdf -xelatex -pvc -output-directory="$OUT" -interaction=nonstopmode "$MAIN" > /tmp/latexmk.log 2>&1 &

# 等待启动
sleep 2

# 检查是否成功启动
if pgrep -f "latexmk.*$MAIN" > /dev/null; then
    echo "✓ latexmk 已启动"
    echo "现在可以编辑文件，保存后会自动编译"
    echo "查看日志: tail -f /tmp/latexmk.log"
    echo ""
    echo "停止方法: pkill -f 'latexmk.*$MAIN'"
else
    echo "✗ 启动失败，查看日志: cat /tmp/latexmk.log"
fi

