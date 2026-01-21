#!/bin/bash
# 完整编译脚本（使用 xelatex + biber）
# 使用方法: ./compile.sh

eval "$(/usr/libexec/path_helper)"

MAIN="main.tex"
OUT="output"

echo "=========================================="
echo "开始编译 LaTeX 文档..."
echo "=========================================="
echo ""

# 创建输出目录
mkdir -p "$OUT"

# 第一步：第一次 xelatex 编译
echo "[1/4] 第一次 XeLaTeX 编译..."
xelatex -output-directory="$OUT" -interaction=nonstopmode "$MAIN" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "✗ 第一次编译失败，查看日志: $OUT/main.log"
    tail -20 "$OUT/main.log" | grep -E "Error|Fatal" | head -5
    exit 1
fi
echo "✓ 完成"
echo ""

# 第二步：运行 biber 处理参考文献
if [ -f "$OUT/main.bcf" ]; then
    echo "[2/4] 运行 Biber 处理参考文献..."
    cd "$OUT"
    biber --input-directory=.. main > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "✗ Biber 失败，查看日志: $OUT/main.blg"
        cd ..
        exit 1
    fi
    cd ..
    echo "✓ 完成"
else
    echo "[2/4] 跳过 Biber（未找到 .bcf 文件）"
fi
echo ""

# 第三步：第二次 xelatex 编译（处理参考文献）
echo "[3/4] 第二次 XeLaTeX 编译（处理参考文献）..."
xelatex -output-directory="$OUT" -interaction=nonstopmode "$MAIN" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "✗ 第二次编译失败，查看日志: $OUT/main.log"
    exit 1
fi
echo "✓ 完成"
echo ""

# 第四步：第三次 xelatex 编译（解决交叉引用）
echo "[4/4] 第三次 XeLaTeX 编译（解决交叉引用）..."
xelatex -output-directory="$OUT" -interaction=nonstopmode "$MAIN" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "✗ 第三次编译失败，查看日志: $OUT/main.log"
    exit 1
fi
echo "✓ 完成"
echo ""

# 检查结果
if [ -f "$OUT/main.pdf" ]; then
    echo "=========================================="
    echo "✓ 编译成功！"
    echo "=========================================="
    
    # 重命名PDF文件
    FINAL_NAME="毕业论文-伍勋高-202333248.pdf"
    mv "$OUT/main.pdf" "$OUT/$FINAL_NAME"
    
    echo "PDF 文件: $OUT/$FINAL_NAME"
    ls -lh "$OUT/$FINAL_NAME" | awk '{print "文件大小:", $5}'
    echo ""
    echo "可以在 Cursor 中打开 output/$FINAL_NAME 查看"
else
    echo "=========================================="
    echo "✗ 编译失败"
    echo "=========================================="
    echo "查看日志: $OUT/main.log"
    exit 1
fi

