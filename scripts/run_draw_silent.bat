@echo off
chcp 65001 >nul
cd /d "%~dp0.."
python -m pip install matplotlib numpy -q 2>nul
python scripts\draw_fedascl_framework.py
