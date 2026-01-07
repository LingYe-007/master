# LaTeXmk 配置文件 - 智能自动编译
# 使用: latexmk -pdf -xelatex -pvc main.tex

$pdf_mode = 5;  # 使用 xelatex
$xelatex = 'xelatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
# 使用 biber（biblatex 需要 biber，不是 bibtex）
# 注意：biber 在 output 目录下运行，但 bib 文件在项目根目录
# 使用绝对路径或相对路径从 output 目录访问
$biber = 'biber --input-directory=.. %O %S';
$bibtex_use = 2;  # 使用 biber（2 = biber, 1 = bibtex, 0 = 都不使用）
$clean_ext = 'bbl synctex.gz bcf blg run.xml';

# 输出目录
$out_dir = 'output';
$aux_dir = 'output';

# 主文件
$pdffile = 'main.pdf';

# 持续预览模式设置
$preview_continuous_mode = 1;
# 不使用外部 PDF 查看器，让 Cursor/VS Code 的内部查看器处理
$pdf_previewer = 'none';  # 不自动打开外部查看器
$pdf_update_method = 0;  # 不自动更新外部查看器

# 即使有错误也继续监听文件变化
$max_repeat = 5;  # 最大重复编译次数
$force_mode = 0;  # 不强制，但确保文件监听正常工作


