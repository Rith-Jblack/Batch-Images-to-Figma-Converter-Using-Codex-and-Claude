@echo off
python3 "%~dp0convert.py"
if errorlevel 1 (
    python "%~dp0convert.py"
)
