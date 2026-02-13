# Image-to-Figma Converter — Technical Document

**Version:** 3.0
**Date:** 2026-02-14
**Author:** Asian Solutions
**Runtime:** Python 3.10+
**Dependency:** Claude CLI (Anthropic) or Codex CLI (OpenAI)

---

## 1. Overview

`convert.py` is a command-line tool that converts UI screenshots into Figma-ready SVG files using Claude AI CLI or OpenAI Codex CLI. It supports parallel processing, live token tracking, multiple AI models, and `.env`-based configuration.

**What it does:**
Screenshot (PNG/JPG) → AI analysis (Claude or Codex) → SVG with named layers + component variants → Import into Figma

---

## 2. Folder Structure

```
py/
├── convert.py              Main converter script
├── run_claude.bat          Windows launcher for Claude provider
├── run_codex.bat           Windows launcher for Codex provider
├── prompt-template.txt     AI prompt template with SVG skeleton
├── .env.claude.example     Claude configuration template (copy to .env)
├── .env.codex.example      Codex configuration template (copy to .env)
├── .env                    Local configuration (gitignored)
├── .gitignore              Git ignore rules
├── DOCUMENT.md             This document
├── config/                 Configuration module
│   ├── __init__.py         load_config() — central config loader
│   ├── constants.py        Default values, model presets, provider IDs
│   └── env_loader.py       Zero-dependency .env file parser
├── 1-images-to-convert/    Input folder — drop screenshots here
│   └── Screenshot_1.png    (sample)
├── 2-image-converted/      Output folder — generated SVGs appear here
│   └── Screenshot_1.svg    (sample output)
└── 3-image-archive/        Archive — converted images move here automatically
```

### File Descriptions

| File | Purpose |
|------|---------|
| `convert.py` | Core script. Reads images, builds prompts, calls AI CLI in parallel, tracks tokens/cost, displays progress. |
| `run_claude.bat` | Double-click launcher for Claude provider. Tries `python3` first, falls back to `python`. |
| `run_codex.bat` | Double-click launcher for Codex provider. Sets `AI_PROVIDER=codex` then runs converter. |
| `prompt-template.txt` | The prompt sent to the AI. Contains SVG skeleton, naming rules, and design constraints. Placeholders: `__IMAGE_PATH__`, `__OUTPUT_PATH__`. |
| `.env.claude.example` | Claude configuration template. Copy to `.env` to use Claude provider. |
| `.env.codex.example` | Codex configuration template. Copy to `.env` to use Codex provider. |
| `.env` | Your local configuration (not committed to git). |
| `config/__init__.py` | Exports `load_config()` which returns a dict with all settings. |
| `config/constants.py` | All default values, model presets, provider IDs, image extensions. |
| `config/env_loader.py` | Custom `.env` file parser (no pip dependencies). |
| `1-images-to-convert/` | Place input screenshots here. Supported: PNG, JPG, JPEG, WEBP, GIF, BMP. |
| `2-image-converted/` | Output directory. Each image produces `{name}.svg`. |
| `3-image-archive/` | Successfully converted images are moved here automatically. |

---

## 3. How It Works

```
┌─────────────────────┐
│  1-images-to-convert │   User drops screenshots
│  ├── page1.png       │
│  ├── page2.jpg       │
│  └── page3.png       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│    convert.py        │   Loads .env + config/
│                      │   Reads prompt-template.txt
│    ThreadPool(3)     │   Launches up to 3 AI CLI processes
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  AI CLI (x3)         │   Claude CLI or Codex CLI per config
│  ├── Reads image     │    1. Analyzes the screenshot
│  ├── Generates SVG   │    2. Creates SVG with Figma layers
│  └── Writes file     │    3. Writes to 2-image-converted/
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  2-image-converted   │   Figma-ready SVGs
│  ├── page1.svg       │   - Named layers (Frame/Header, Frame/Content)
│  ├── page2.svg       │   - Component variants (Hover/Active/Pressed)
│  └── page3.svg       │   - Prototyping annotations (data-* attributes)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  3-image-archive     │   Converted images moved here
│  ├── page1.png       │   (auto-archived on success)
│  ├── page2.jpg       │
│  └── page3.png       │
└─────────────────────┘
```

---

## 4. Configuration

### Config Priority (highest to lowest)

1. **System environment variables** (e.g., `CLAUDE_MODEL=opus python3 convert.py`)
2. **`.env` file** values
3. **Built-in defaults** from `config/constants.py`

### Environment Variables

#### Provider Selection

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_PROVIDER` | `claude` | AI CLI to use: `claude` or `codex` |

#### Claude CLI Settings (when `AI_PROVIDER=claude`)

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAUDE_MODEL` | `claude-sonnet-4-5-20250929` | Claude model to use |
| `CLAUDE_MAX_TURNS` | `15` | Max AI conversation turns per image |
| `CLAUDE_PARALLEL` | `3` | Max concurrent conversions |
| `CLAUDE_DEBUG` | `0` | Set to `1` for verbose output |
| `CLAUDE_TIMEOUT` | `600` | Timeout per image in seconds |

#### Codex CLI Settings (when `AI_PROVIDER=codex`)

| Variable | Default | Description |
|----------|---------|-------------|
| `CODEX_MODEL` | *(Codex default)* | Codex model to use (leave empty for Codex CLI default) |
| `CODEX_SANDBOX` | `workspace-write` | Codex sandbox level |
| `CODEX_PARALLEL` | `3` | Max concurrent conversions |
| `CODEX_DEBUG` | `0` | Set to `1` for verbose output |
| `CODEX_TIMEOUT` | `600` | Timeout per image in seconds |

#### Generic Fallbacks (used if provider-specific vars not set)

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_MODEL` | — | Fallback model name |
| `AI_PARALLEL` | `3` | Fallback parallel count |
| `AI_DEBUG` | `0` | Fallback debug flag |
| `AI_TIMEOUT` | `600` | Fallback timeout |

#### Shared Paths

| Variable | Default | Description |
|----------|---------|-------------|
| `INPUT_DIR` | `../1-images-to-convert` | Input image directory |
| `OUTPUT_DIR` | `../2-image-converted` | Output SVG directory |
| `ARCHIVE_DIR` | `./3-image-archive` | Archive for converted images |
| `PROMPT_TEMPLATE` | `../prompt-template.txt` | Prompt template file |

### Using .env File

```bash
# For Claude provider:
cp .env.claude.example .env

# For Codex provider:
cp .env.codex.example .env

# Edit .env with your settings — uncomment and change values as needed
```

### Model Comparison

#### Claude Models

| Model | ID | Speed | Quality | Cost/Image |
|-------|----|-------|---------|------------|
| Sonnet 4.5 | `claude-sonnet-4-5-20250929` | ~1 min | Good | ~$0.60 |
| Opus 4.6 | `claude-opus-4-6` | ~3 min | Best | ~$1.50 |
| Haiku 4.5 | `claude-haiku-4-5-20251001` | ~30s | Basic | ~$0.10 |

#### Codex Models

| Model | ID | Speed | Quality | Note |
|-------|----|-------|---------|------|
| *(default)* | — | ~2 min | Good | Recommended — uses Codex CLI default model |
| O4 Mini | `o4-mini` | ~1 min | Good | Requires API account |
| O3 | `o3` | ~2 min | Higher | Requires API account |

> **Note:** Some Codex models (e.g., `o3`, `o4-mini`) require an OpenAI API account. If you're using a ChatGPT account, leave `CODEX_MODEL` empty to use the Codex CLI default.

---

## 5. Usage

### Quick Start

```bash
# 1. Drop images into 1-images-to-convert/
# 2. Run the converter
python3 convert.py
```

### Windows (double-click)

```
run_claude.bat      # Run with Claude provider
run_codex.bat       # Run with Codex provider
```

### Using .env File (Recommended)

```bash
# For Claude:
cp .env.claude.example .env

# For Codex:
cp .env.codex.example .env

# Then just run — settings come from .env
python3 convert.py
```

### Override Settings (env vars)

```bash
# Use Opus for highest quality
CLAUDE_MODEL=claude-opus-4-6 python3 convert.py

# Use Codex instead of Claude
AI_PROVIDER=codex python3 convert.py

# Use Codex with specific model (requires API account for o3/o4-mini)
AI_PROVIDER=codex CODEX_MODEL=o3 python3 convert.py

# Process 5 images at once
CLAUDE_PARALLEL=5 python3 convert.py

# Sequential mode (1 at a time)
CLAUDE_PARALLEL=1 python3 convert.py

# Debug mode (see CLI output)
CLAUDE_DEBUG=1 python3 convert.py

# Custom folders
INPUT_DIR=/path/to/screenshots OUTPUT_DIR=/path/to/output python3 convert.py
```

### Windows PowerShell

```powershell
$env:AI_PROVIDER="codex"
python3 convert.py

# Or with a specific model (requires API account):
$env:AI_PROVIDER="codex"
$env:CODEX_MODEL="o3"
python3 convert.py
```

---

## 6. Output Format

Each run displays:

```
  +=====================================================+
  |     Image -> Figma Design Converter                 |
  |     Professional Component Generator   (Python)     |
  +=====================================================+

  Provider:  CLAUDE
  Source:    D:\project\1-images-to-convert
  Output:    D:\project\2-image-converted
  Model:     claude-sonnet-4-5-20250929
  Turns:     15
  Images:    3 file(s) found
  Parallel:  3 concurrent
  Est:       ~1m 0s
  Token:     live token tracking enabled

  ----------------------------------------------------

    [1] page1.png
    [2] page2.png
    [3] page3.png

  [==============--------------------------] 33%  [OK] page1.svg (10KB, 58s, 289.7K tok, $0.6214)
    Token: 289.7K total | Cost: $0.6214
  [=============================-----------] 66%  [OK] page2.svg (12KB, 1m 2s, 301.2K tok, $0.6445)
    Token: 590.9K total | Cost: $1.2659
  [========================================] 100% [OK] page3.svg (9KB, 55s, 278.4K tok, $0.5890)
    Token: 869.3K total | Cost: $1.8549

  ----------------------------------------------------

  +=====================================================+
  |   ALL IMAGES CONVERTED SUCCESSFULLY!                |
  +=====================================================+

  Results:
    Total images:   3
    Converted:      3
    Total time:     1m 5s
    Total tokens:   869.3K
    Total cost:     $1.8549
```

### Per-Image Result Fields

| Field | Example | Description |
|-------|---------|-------------|
| Status | `[OK]` / `[FAIL]` | Conversion success or failure |
| File | `page1.svg` | Output filename |
| Size | `10KB` | SVG file size |
| Time | `58s` | Wall-clock time for this image |
| Tokens | `289.7K tok` | Total tokens used (input + cache + output) |
| Cost | `$0.6214` | USD cost for this image |

### Live Running Total

After each image completes, a running total is displayed:
```
Token: 590.9K total | Cost: $1.2659
```

---

## 7. SVG Output Specification

The generated SVG contains two panels:

### LEFT Panel — Main UI (1:1 copy of screenshot)

```
Frame/Main
├── Frame/Header          Title bar, icon, subtitle
└── Frame/Content         Input fields, buttons, dropdowns, progress bars
```

### RIGHT Panel — Component Variants (for Figma prototyping)

```
Frame/ComponentVariants
├── Variant/Dropdown/Closed
├── Variant/Dropdown/Hover
├── Variant/Dropdown/Open
├── Variant/OptionItem/Default
├── Variant/OptionItem/Hover
├── Variant/OptionItem/Selected
├── Variant/Button/BrowseStates     (Default | Hover | Pressed)
└── Variant/Button/ActionStates     (Default | Hover | Pressed)
```

### Design Rules Enforced

| Rule | Reason |
|------|--------|
| No `<filter>` elements | Figma rasterizes SVG filters, causing blurry text |
| Unicode emoji for icons | `<symbol>` path icons render as crude squares in Figma |
| No `opacity="0"` groups | Hidden groups still import as Figma layers |
| `<linearGradient>` backgrounds | Matches original screenshot appearance |
| `stroke-width="1.5" opacity="0.15"` borders | Subtle, professional container borders |
| `viewBox="0 0 1160 680+"` | Wide enough for both panels, tall enough for variants |

---

## 8. Architecture

### Code Structure

```
config/
├── __init__.py     load_config()       — Central config loader (.env + env vars + defaults)
├── constants.py    Defaults            — All magic values, model presets, provider IDs
└── env_loader.py   load_dotenv()       — Zero-dependency .env parser

convert.py
├── Lines   1-32    Imports + config loading
├── Lines  35-78    Utilities (colors, progress bar, time/token formatting)
├── Lines  81-134   Provider abstraction (command building, prompt adaptation)
├── Lines 137-207   Token parsing (Claude JSON, Codex JSONL, dispatcher)
├── Lines 210-270   convert_image()     — Thread-safe single image conversion
└── Lines 273-457   main()              — Entry point, parallel orchestration
```

### Key Functions

**`load_config() -> dict`** (in `config/__init__.py`)
Loads `.env` file, reads environment variables with provider-specific fallback chains, returns normalized config dict.

**`build_command(prompt, img, cfg) -> list`**
Dispatches to `build_claude_command()` or `build_codex_command()` based on provider.

**`adapt_prompt(prompt_template, img, output_svg, cfg) -> str`**
Adapts prompt for the provider. Claude reads images via Read tool; Codex receives images via `--image` flag.

**`parse_token_usage(stdout, provider) -> dict`**
Dispatches to `parse_claude_tokens()` (JSON) or `parse_codex_tokens()` (JSONL).

**`convert_image(img, prompt_template, cfg) -> tuple`**
Thread-safe function that converts a single image. Returns `(filename, success, elapsed, size_kb, error, tokens)`.

**`main()`**
Orchestrates the full pipeline: load config, validate, collect images, launch `ThreadPoolExecutor`, print results, display summary.

### Parallel Processing

```python
ThreadPoolExecutor(max_workers=cfg["parallel"])  # default: 3
├── Thread 1: convert_image(page1.png)  →  page1.svg
├── Thread 2: convert_image(page2.png)  →  page2.svg
└── Thread 3: convert_image(page3.png)  →  page3.svg
```

Results are printed as each thread finishes (not in input order). The progress bar and token totals update live.

### CLI Commands Per Provider

**Claude:**
```bash
claude -p "<prompt>" \
  --allowedTools Read,Write,Edit \
  --max-turns 15 \
  --model claude-sonnet-4-5-20250929 \
  --output-format json
```

**Codex:**
```bash
codex exec \
  --full-auto \
  --sandbox workspace-write \
  --json \
  --image /path/to/image.png \
  -
# prompt is piped via stdin (avoids OS command-line length limits)
```

---

## 9. Prompt Template

File: `prompt-template.txt`

The prompt instructs the AI to:

1. **Read** the screenshot at `__IMAGE_PATH__` (Claude uses Read tool; Codex receives via `--image`)
2. **Write** an SVG to `__OUTPUT_PATH__`
3. Generate **two panels**: LEFT (main UI copy) + RIGHT (component variants)
4. Follow strict rules: no filters, emoji icons, gradients, subtle borders
5. Use provided **SVG skeleton** as the structural template
6. Respond with `CONVERSION_COMPLETE` when done

Placeholders replaced at runtime:
- `__IMAGE_PATH__` → Absolute path to input image
- `__OUTPUT_PATH__` → Absolute path to output SVG

---

## 10. Importing into Figma

After conversion:

1. Open **Figma** → New File
2. **File** → **Place Image** (or drag and drop)
3. Select SVG files from `2-image-converted/`
4. All layers and components will be **editable**:
   - Layers are named with Figma conventions (`Frame/Header`, `Variant/Button/Hover`)
   - Component variants are ready for prototyping
   - Interaction annotations via `data-*` attributes

---

## 11. Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `claude CLI not found` | Claude CLI not installed | Install: `npm install -g @anthropic-ai/claude-code` |
| `codex CLI not found` | Codex CLI not installed | Install: `npm install -g @openai/codex` |
| `SyntaxError: f-string` | Running with Python 2 | Use `python3 convert.py` or `run.bat` |
| `EOFError: EOF` | `input()` in non-interactive shell | Normal when running from scripts; ignore |
| `[FAIL]` on an image | AI couldn't generate valid SVG | Check the error message; re-run or try a different model |
| `model not supported` (Codex) | Model unavailable for your account type | Unset `CODEX_MODEL` to use the Codex CLI default, or use a supported model |
| Blurry text in Figma | SVG has `<filter>` elements | Prompt enforces no-filter rule; re-run |
| Timeout (600s) | Image too complex | Increase `CLAUDE_TIMEOUT` or `CODEX_TIMEOUT` in .env |

---

## 12. Requirements

- **Python:** 3.10 or higher
- **AI CLI:** One of:
  - Claude CLI: Installed and authenticated (`claude` in PATH)
  - Codex CLI: Installed and authenticated (`codex` in PATH)
- **OS:** Windows, macOS, Linux
- **Network:** Internet connection (AI API calls)
- **No pip dependencies** — uses only Python standard library

---

## 13. Languages

This documentation is available in multiple languages:

| Language | File |
|----------|------|
| English | [README.md](README.md) |
| ខ្មែរ (Khmer) | [README_KH.md](README_KH.md) |
