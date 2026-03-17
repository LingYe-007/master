@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo Installing packages...
python -m pip install matplotlib numpy -q
if %errorlevel% neq 0 (
    echo Failed to install. Try: pip install matplotlib numpy
    pause
    exit /b 1
)
echo Running draw script...
python scripts\draw_fedascl_framework.py
if %errorlevel% neq 0 (
    echo Failed to run script.
    pause
    exit /b 1
)
echo Done. Image saved to images\fedascl_framework.png
pause
