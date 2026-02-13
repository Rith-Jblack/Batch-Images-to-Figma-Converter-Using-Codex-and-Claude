# Image to Figma Converter (Python)

Convert UI screenshots into **Figma-ready SVG files** with named layers, component variants, and prototyping annotations — powered by Claude AI or OpenAI Codex.

```
Screenshot (PNG/JPG) → AI Analysis → SVG with Figma layers + component variants
```

## Quick Start

```bash
# 1. Drop screenshots into the input folder
cp ~/screenshots/*.png ../1-images-to-convert/

# 2. (Optional) Configure via .env
cp .env.claude.example .env    # For Claude
cp .env.codex.example .env     # For Codex

# 3. Run
python3 convert.py
```

### Windows (double-click)

```
run_claude.bat      # Run with Claude provider
run_codex.bat       # Run with Codex provider
```

## Configuration

Copy `.env.claude.example` or `.env.codex.example` to `.env` and uncomment the settings you want to change.

**Priority:** Environment variables > `.env` file > defaults

```ini
# AI Provider: "claude" or "codex"
AI_PROVIDER=claude

# Claude settings
CLAUDE_MODEL=claude-sonnet-4-5-20250929
CLAUDE_MAX_TURNS=15
CLAUDE_PARALLEL=3
CLAUDE_DEBUG=0
CLAUDE_TIMEOUT=600

# Codex settings
# CODEX_MODEL=             # leave empty for Codex CLI default (recommended)
CODEX_SANDBOX=workspace-write
CODEX_PARALLEL=3

# Paths
INPUT_DIR=../1-images-to-convert
OUTPUT_DIR=../2-image-converted
PROMPT_TEMPLATE=../prompt-template.txt
```

### Override via CLI

```bash
CLAUDE_MODEL=claude-opus-4-6 python3 convert.py        # Opus quality
AI_PROVIDER=codex python3 convert.py                    # Use Codex
CLAUDE_PARALLEL=5 python3 convert.py                    # 5 concurrent
CLAUDE_DEBUG=1 python3 convert.py                       # Debug output
```

## Models

| Model | Speed | Quality | Cost/Image |
|-------|-------|---------|------------|
| `claude-sonnet-4-5-20250929` | ~1 min | Good | ~$0.60 |
| `claude-opus-4-6` | ~3 min | Best | ~$1.50 |
| `claude-haiku-4-5-20251001` | ~30s | Basic | ~$0.10 |
| *(Codex default)* | ~2 min | Good | — |
| `o4-mini` (Codex) | ~1 min | Good | API account required |
| `o3` (Codex) | ~2 min | Higher | API account required |

## Project Structure

```
py/
├── convert.py              Main converter script
├── run_claude.bat          Windows launcher (Claude)
├── run_codex.bat           Windows launcher (Codex)
├── .env.claude.example     Claude config template (copy to .env)
├── .env.codex.example      Codex config template (copy to .env)
├── prompt-template.txt     AI prompt with SVG skeleton
├── DOCUMENT.md             Full technical documentation
├── config/
│   ├── __init__.py         load_config() — central config loader
│   ├── constants.py        Default values, model presets, provider IDs
│   └── env_loader.py       Zero-dependency .env parser
├── 1-images-to-convert/    Drop input images here
├── 2-image-converted/      Generated SVGs appear here
└── 3-image-archive/        Converted images auto-archived here
```

## SVG Output

Each SVG has two panels side-by-side:

| Panel | Content |
|-------|---------|
| **LEFT** — Main UI | 1:1 copy of screenshot with named Figma layers |
| **RIGHT** — Variants | Button/Dropdown states (Default, Hover, Pressed, Active) |

## Importing into Figma

1. Open **Figma** → New File
2. **File** → **Place Image** (or drag and drop)
3. Select SVGs from `2-image-converted/`
4. All layers and components are editable

## Requirements

- **Python** 3.10+
- **AI CLI** — [Claude CLI](https://docs.anthropic.com/en/docs/claude-code) or [Codex CLI](https://github.com/openai/codex)
- **No pip dependencies** — stdlib only

## Supported Formats

PNG, JPG, JPEG, WEBP, GIF, BMP

## Docs

See [DOCUMENT.md](DOCUMENT.md) for full technical documentation.

## Languages

This documentation is available in:
- **English** — [README.md](README.md)
- **ខ្មែរ (Khmer)** — [README_KH.md](README_KH.md)
