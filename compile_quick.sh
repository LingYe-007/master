#!/bin/bash

# 快速编译脚本 - 只运行一次 XeLaTeX（适合快速查看格式变化）
# 使用：./compile_quick.sh

MAIN="main.tex"
OUT="output"

echo "=========================================="
echo "快速编译 LaTeX 文档（单次编译）..."
echo "=========================================="
echo ""

# 确保输出目录存在
mkdir -p "$OUT"

# 进入项目根目录
cd "$(dirname "$0")"

# 只运行一次 XeLaTeX（最快）
echo "[1/1] 运行 XeLaTeX..."
xelatex -interaction=nonstopmode -output-directory="$OUT" "$MAIN" > /dev/null 2>&1

# 即使有警告也继续（只要生成了PDF）
if [ -f "$OUT/main.pdf" ]; then
    echo "✓ 编译完成（快速模式）"
    echo ""
    ls -lh "$OUT/main.pdf" | awk '{print "PDF:", $5, "更新时间:", $6, $7, $8}'
    echo ""
    echo "注意：快速模式不更新参考文献和目录页码"
    echo "如需完整编译，请使用 ./compile.sh"
else
    echo "✗ 编译失败，查看日志: $OUT/main.log"
    tail -30 "$OUT/main.log" | grep -E "Error|Fatal|!" | head -10
fi

