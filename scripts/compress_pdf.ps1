# 使用 Ghostscript 压缩已生成的 PDF，目标体积 < 30MB
# 需要先安装 Ghostscript: winget install Artifex.Ghostscript
# 用法: .\scripts\compress_pdf.ps1  或  .\scripts\compress_pdf.ps1 -InputPdf output\main.pdf

param(
    [string]$InputPdf = "output\伍勋高-202333248.pdf",
    [string]$OutputPdf = "output\伍勋高-202333248_compressed.pdf"
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
if (-not (Split-Path -IsAbsolute $InputPdf))  { $InputPdf  = Join-Path $root $InputPdf }
if (-not (Split-Path -IsAbsolute $OutputPdf)) { $OutputPdf = Join-Path $root $OutputPdf }

$gs = Get-Command gswin64c -ErrorAction SilentlyContinue
if (-not $gs) {
    Write-Host "未找到 Ghostscript (gswin64c)。请安装: winget install Artifex.Ghostscript"
    exit 1
}

if (-not (Test-Path $InputPdf)) {
    Write-Host "输入文件不存在: $InputPdf"
    exit 1
}

$sizeBefore = (Get-Item $InputPdf).Length / 1MB
Write-Host "正在压缩 PDF: $InputPdf -> $OutputPdf (压缩前: $([math]::Round($sizeBefore, 2)) MB)"

& gswin64c -sDEVICE=pdfwrite `
  -dCompatibilityLevel=1.4 `
  -dPDFSETTINGS=/ebook `
  -dNOPAUSE -dQUIET -dBATCH `
  -sOutputFile=$OutputPdf $InputPdf

$sizeAfter = (Get-Item $OutputPdf).Length / 1MB
Write-Host "压缩完成。输出: $OutputPdf (约 $([math]::Round($sizeAfter, 2)) MB)"
if ($sizeAfter -lt 30) { Write-Host "已低于 30MB，可将该文件重命名替换原稿。" }
