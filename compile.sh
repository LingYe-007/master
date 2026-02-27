#!/bin/bash
# 编译脚本：优先使用 latexmk（自动判断需运行的次数，通常更快）
# 使用: ./compile.sh

eval "$(/usr/libexec/path_helper 2>/dev/null)" || true

MAIN="main.tex"
OUT="output"
FINAL_NAME="伍勋高-202333248.pdf"

mkdir -p "$OUT"

echo "=========================================="
echo "开始编译 LaTeX 文档..."
echo "=========================================="
echo ""

# 优先使用 latexmk：只运行必要的次数，通常比固定 4 步更快
if command -v latexmk >/dev/null 2>&1; then
    echo "使用 latexmk 编译（自动判断运行次数）..."
    latexmk -pdf -xelatex -outdir="$OUT" -interaction=nonstopmode -silent "$MAIN" 2>&1 | grep -E "^(Latexmk|Output written|xelatex|biber)" || true
    OK=$?
else
    OK=1
fi

# 若 latexmk 未安装或失败，则回退到分步编译
if [ $OK -ne 0 ] || [ ! -f "$OUT/main.pdf" ]; then
    echo "使用分步编译..."
    echo "[1/4] 第一次 XeLaTeX..."
    xelatex -output-directory="$OUT" -interaction=nonstopmode "$MAIN" >/dev/null 2>&1
    [ $? -ne 0 ] && echo "✗ 第一次编译失败，查看 $OUT/main.log" && exit 1
    if [ -f "$OUT/main.bcf" ]; then
        echo "[2/4] Biber..."
        (cd "$OUT" && biber --input-directory=.. main) >/dev/null 2>&1
    fi
    echo "[3/4] 第二次 XeLaTeX..."
    xelatex -output-directory="$OUT" -interaction=nonstopmode "$MAIN" >/dev/null 2>&1
    echo "[4/4] 第三次 XeLaTeX..."
    xelatex -output-directory="$OUT" -interaction=nonstopmode "$MAIN" >/dev/null 2>&1
fi

if [ -f "$OUT/main.pdf" ]; then
    cp "$OUT/main.pdf" "$OUT/$FINAL_NAME"
    echo ""
    echo "=========================================="
    echo "✓ 编译成功"
    echo "=========================================="
    echo "PDF: $OUT/$FINAL_NAME"
    ls -lh "$OUT/$FINAL_NAME" | awk '{print "大小:", $5}'
else
    echo "=========================================="
    echo "✗ 编译失败，查看 $OUT/main.log"
    echo "=========================================="
    exit 1
fi
