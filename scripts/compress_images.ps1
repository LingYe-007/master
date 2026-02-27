# 一次性压缩 images/ 下过大图片（长边>1600px 或 >800KB），原图备份到 images/backup/
# 用法：在项目根执行  .\scripts\compress_images.ps1
# 后续正常编译不需要再运行此脚本。

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$root = Split-Path $PSScriptRoot -Parent
$imagesDir = Join-Path $root "images"
$backupDir = Join-Path $imagesDir "backup"
$maxSide = 1600
$minSizeToShrink = 800 * 1024   # 800KB
$jpgQuality = 88

if (-not (Test-Path $imagesDir)) { Write-Host "未找到 images 目录"; exit 1 }
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$jpegCodec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
$qualityParam = [System.Drawing.Imaging.EncoderParameter]::new([System.Drawing.Imaging.Encoder]::Quality, $jpgQuality)
$encoderParams = [System.Drawing.Imaging.EncoderParameters]::new(1)
$encoderParams.Param[0] = $qualityParam

$count = 0
Get-ChildItem $imagesDir -File | Where-Object { $_.Extension -match "\.(png|jpg|jpeg)$" } | Sort-Object Name | ForEach-Object {
    $path = $_.FullName
    $sizeKb = [math]::Round($_.Length / 1024, 0)
    $needShrink = $_.Length -gt $minSizeToShrink
    try {
        $img = [System.Drawing.Image]::FromFile($path)
        $w = $img.Width
        $h = $img.Height
        $img.Dispose()
    } catch {
        Write-Host "  跳过（无法打开）: $($_.Name) - $_"
        return
    }
    $needShrink = $needShrink -or ($w -gt $maxSide) -or ($h -gt $maxSide)
    if (-not $needShrink) { return }

    # 备份
    $backupPath = Join-Path $backupDir $_.Name
    if (-not (Test-Path $backupPath) -or (Get-Item $backupPath).Length -ne $_.Length) {
        Copy-Item $path $backupPath -Force
        Write-Host "  已备份: $($_.Name)"
    }

    $img = [System.Drawing.Image]::FromFile($path)
    $nw = $w; $nh = $h
    if ($w -gt $maxSide -or $h -gt $maxSide) {
        if ($w -ge $h) { $nw = $maxSide; $nh = [int]($h * $maxSide / $w) }
        else            { $nh = $maxSide; $nw = [int]($w * $maxSide / $h) }
    }
    $bmp = New-Object System.Drawing.Bitmap($nw, $nh)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.DrawImage($img, 0, 0, $nw, $nh)
    $g.Dispose()
    $img.Dispose()

    $ext = $_.Extension.ToLower()
    if ($ext -eq ".jpg" -or $ext -eq ".jpeg") {
        $bmp.Save($path, $jpegCodec, $encoderParams)
    } else {
        $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    $bmp.Dispose()
    $newKb = [math]::Round((Get-Item $path).Length / 1024, 0)
    Write-Host "  已压缩: $($_.Name)  $sizeKb KB -> $newKb KB"
    $script:count++
}
Write-Host "处理完成，共压缩 $count 张。请重新编译论文生成 PDF。"
if ($count -gt 0) { Write-Host "原图已备份至 images/backup/ ，如需恢复可从中复制回来。" }
