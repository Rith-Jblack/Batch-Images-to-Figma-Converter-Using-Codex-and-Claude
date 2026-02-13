@echo off
pushd "%~dp0"
set AI_PROVIDER=codex
python3 "%CD%\convert.py"
if errorlevel 1 (
    python "%CD%\convert.py"
)
popd
