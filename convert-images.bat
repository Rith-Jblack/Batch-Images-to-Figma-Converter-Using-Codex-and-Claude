@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

:: =============================================================================
::  Image to Figma Professional Design Converter (Windows CMD)
::  Uses Claude CLI to analyze UI screenshots and generate professional
::  Figma-ready SVG designs with proper component structure
:: =============================================================================

:: -- Configuration ------------------------------------------------------------
pushd "%~dp0"
set "SCRIPT_DIR=%CD%"
popd

if not defined INPUT_DIR  set "INPUT_DIR=%SCRIPT_DIR%\1-images-to-convert"
if not defined OUTPUT_DIR set "OUTPUT_DIR=%SCRIPT_DIR%\2-image-converted"
if not defined CLAUDE_MODEL set "CLAUDE_MODEL=o3"
if not defined CLAUDE_MAX_TURNS set "CLAUDE_MAX_TURNS=10"
if not defined CLAUDE_DEBUG set "CLAUDE_DEBUG=0"

set "PROMPT_TPL=%SCRIPT_DIR%\prompt-template.txt"

:: Allow running from within another Claude session
set "CLAUDECODE="

:: -- Header -------------------------------------------------------------------
cls
echo.
echo   +=====================================================+
echo   ^|                                                     ^|
echo   ^|     Image -^> Figma Design Converter                 ^|
echo   ^|     Professional Component Generator                ^|
echo   ^|                                                     ^|
echo   +=====================================================+
echo.

:: -- Validate prompt template -------------------------------------------------
if not exist "%PROMPT_TPL%" (
    echo   [ERROR] Missing prompt-template.txt
    echo     %PROMPT_TPL%
    echo.
    pause
    exit /b 1
)

:: -- Setup output dir ---------------------------------------------------------
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

:: -- Collect image files ------------------------------------------------------
set "total=0"
set "idx=0"
for %%e in (png jpg jpeg webp gif bmp) do (
    for %%f in ("%INPUT_DIR%\*.%%e") do (
        if exist "%%f" (
            set "IMG_!idx!=%%~ff"
            set "NAME_!idx!=%%~nf"
            set "FILE_!idx!=%%~nxf"
            set /a "idx+=1"
        )
    )
)
set "total=%idx%"

if %total% equ 0 (
    echo   [ERROR] No images found in:
    echo     %INPUT_DIR%
    echo.
    echo   Supported: PNG, JPG, JPEG, WEBP, GIF, BMP
    echo.
    pause
    exit /b 1
)

:: -- Display config -----------------------------------------------------------
echo   Source:  %INPUT_DIR%
echo   Output:  %OUTPUT_DIR%
echo   Model:   %CLAUDE_MODEL%
echo   Turns:   %CLAUDE_MAX_TURNS%
echo   Images:  %total% file(s) found

:: Estimate time based on model (~2min Sonnet, ~3min Opus, ~30s Haiku)
set "est_min=2"
echo %CLAUDE_MODEL% | findstr /i "opus" >nul && set "est_min=3"
echo %CLAUDE_MODEL% | findstr /i "haiku" >nul && set "est_min=0"
set /a "est_total=est_min * total"
if %est_total% equ 0 (
    set /a "est_sec=30 * total"
    echo   Est:     ~!est_sec!s
) else (
    echo   Est:     ~%est_total%min
)
echo.
echo   ----------------------------------------------------
echo.

set "success_count=0"
set "fail_count=0"
set "failed_list="

:: -- Main conversion loop -----------------------------------------------------
for /l %%i in (0,1,%idx%) do (
    if %%i lss %total% (
        set /a "current=%%i+1"

        echo   [!current!/%total%] Converting: !FILE_%%i!
        echo     Status: Sending to Claude AI...

        set "output_svg=%OUTPUT_DIR%\!NAME_%%i!.svg"

        :: Build prompt from template - replace placeholders
        set "promptFile=%TEMP%\figma_prompt_%%i.txt"
        powershell -NoProfile -Command "$t = [IO.File]::ReadAllText('%PROMPT_TPL%'); $t = $t.Replace('__IMAGE_PATH__','!IMG_%%i!').Replace('__OUTPUT_PATH__','!output_svg!'); [IO.File]::WriteAllText('!promptFile!',$t)"

        echo     Status: AI analyzing screenshot...

        if "!CLAUDE_DEBUG!"=="1" (
            echo     CMD: claude -p [prompt] --allowedTools Read,Write,Edit --max-turns %CLAUDE_MAX_TURNS% --model %CLAUDE_MODEL%
        )

        :: Execute Claude CLI via PowerShell (handles long prompt strings)
        powershell -NoProfile -Command "$p = [IO.File]::ReadAllText('!promptFile!'); & claude -p $p --allowedTools 'Read,Write,Edit' --max-turns %CLAUDE_MAX_TURNS% --model %CLAUDE_MODEL%" >nul 2>&1

        :: Clean up temp file
        if exist "!promptFile!" del /q "!promptFile!"

        echo     Status: Checking output...

        :: Check result
        if exist "!output_svg!" (
            for %%s in ("!output_svg!") do set /a "fsize=%%~zs / 1024"
            set /a "success_count+=1"
            echo   [OK] !NAME_%%i!.svg ^(!fsize!KB^)
        ) else (
            set /a "fail_count+=1"
            set "failed_list=!failed_list! !FILE_%%i!"
            echo   [FAIL] !FILE_%%i!
        )
        echo.
    )
)

:: -- Final Summary ------------------------------------------------------------
echo   ----------------------------------------------------
echo.

if %fail_count% equ 0 (
    echo   +=====================================================+
    echo   ^|                                                     ^|
    echo   ^|   ALL IMAGES CONVERTED SUCCESSFULLY^!                ^|
    echo   ^|                                                     ^|
    echo   +=====================================================+
) else (
    echo   +=====================================================+
    echo   ^|   CONVERSION COMPLETE WITH ERRORS                   ^|
    echo   +=====================================================+
)
echo.

echo   Results:
echo     Total images:   %total%
echo     Converted:      %success_count%
if %fail_count% gtr 0 (
    echo     Failed:         %fail_count%
)
echo.

if %fail_count% gtr 0 (
    echo   Failed files:
    for %%f in (%failed_list%) do (
        echo     X %%f
    )
    echo.
)

echo   Import into Figma:
echo     1. Open Figma ^> New File
echo     2. File ^> Place Image (or drag and drop)
echo     3. Select SVG files from:
echo        %OUTPUT_DIR%
echo     4. All layers and components will be editable
echo.
echo   SVG layers named with Figma conventions
echo   Colors extracted as CSS variables for easy theming
echo.
echo   ====================================================
echo   Press any key to close this window...
echo   ====================================================
pause >nul

endlocal
exit /b 0
