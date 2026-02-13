@echo off
pushd "%~dp0"
python3 "%CD%\convert.py"
if errorlevel 1 (
    python "%CD%\convert.py"
)
popd
