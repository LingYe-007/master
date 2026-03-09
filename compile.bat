@echo off
REM 完整编译脚本：在项目根目录编译以正确解析参考文献
cd /d "%~dp0"

echo [1/4] 第一次 XeLaTeX...
xelatex -interaction=nonstopmode main.tex > nul
echo [2/4] Biber 处理参考文献...
biber main > nul 2>&1
echo [3/4] 第二次 XeLaTeX...
xelatex -interaction=nonstopmode main.tex > nul
echo [4/4] 第三次 XeLaTeX...
xelatex -interaction=nonstopmode main.tex

if exist output (
    copy main.pdf output\main.pdf > nul
    echo.
    echo PDF 已复制到 output\main.pdf
)

echo.
echo 编译完成。
