# 完整编译 LaTeX 并输出 PDF：伍勋高-202333248.pdf
# 使用前请确保已安装 TeX Live 或 MiKTeX，并将 xelatex、biber 加入 PATH（或在本机 TeX 命令行中运行）

$ErrorActionPreference = "Stop"
$Main = "main.tex"
$OutDir = "output"
$FinalName = "伍勋高-202333248.pdf"
$OutDirFull = Join-Path (Get-Location) $OutDir

New-Item -ItemType Directory -Force -Path $OutDirFull | Out-Null

function Run-XeLaTeX {
    xelatex -output-directory="$OutDirFull" -interaction=nonstopmode $Main
    if ($LASTEXITCODE -ne 0) { throw "XeLaTeX 编译失败，请查看 $OutDirFull\main.log" }
}

Write-Host "=========================================="
Write-Host "开始编译 LaTeX 文档..."
Write-Host "=========================================="

Write-Host "[1/4] 第一次 XeLaTeX..."
Run-XeLaTeX

if (Test-Path (Join-Path $OutDirFull "main.bcf")) {
    Write-Host "[2/4] Biber 处理参考文献..."
    Push-Location $OutDirFull
    biber --input-directory=.. main
    Pop-Location
}

Write-Host "[3/4] 第二次 XeLaTeX..."
Run-XeLaTeX
Write-Host "[4/4] 第三次 XeLaTeX..."
Run-XeLaTeX

$pdfPath = Join-Path $OutDirFull "main.pdf"
if (Test-Path $pdfPath) {
    $dest = Join-Path $OutDirFull $FinalName
    Copy-Item -Path $pdfPath -Destination $dest -Force
    Copy-Item -Path $pdfPath -Destination $FinalName -Force  # 项目根目录也保留一份
    Write-Host ""
    Write-Host "=========================================="
    Write-Host "✓ 编译成功"
    Write-Host "=========================================="
    Write-Host "PDF: $OutDirFull\$FinalName"
    Write-Host "PDF: $FinalName (项目根目录)"
    Get-Item $dest | ForEach-Object { Write-Host "大小: $([math]::Round($_.Length/1KB, 2)) KB" }
} else {
    Write-Host "=========================================="
    Write-Host "✗ 编译失败，请查看 $OutDirFull\main.log"
    Write-Host "=========================================="
    exit 1
}
