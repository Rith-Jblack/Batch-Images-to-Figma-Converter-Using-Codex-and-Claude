# Image to Figma Converter (Python)

បម្លែងរូបភាពថតអេក្រង់ UI ទៅជា **ឯកសារ SVG សម្រាប់ Figma** ដែលមានស្រទាប់មានឈ្មោះ, component variants, និង prototyping annotations — ដំណើរការដោយ Claude AI ឬ OpenAI Codex។

```
រូបភាពថតអេក្រង់ (PNG/JPG) → វិភាគដោយ AI → SVG ជាមួយស្រទាប់ Figma + component variants
```

## ចាប់ផ្តើមរហ័ស

```bash
# 1. ដាក់រូបភាពថតអេក្រង់ទៅក្នុង folder បញ្ចូល
cp ~/screenshots/*.png ../1-images-to-convert/

# 2. (ជម្រើស) កំណត់រចនាសម្ព័ន្ធតាម .env
cp .env.claude.example .env    # សម្រាប់ Claude
cp .env.codex.example .env     # សម្រាប់ Codex

# 3. ដំណើរការ
python3 convert.py
```

### Windows (ចុចពីរដង)

```
run_claude.bat      # ដំណើរការជាមួយ Claude
run_codex.bat       # ដំណើរការជាមួយ Codex
```

## ការកំណត់រចនាសម្ព័ន្ធ

ចម្លង `.env.claude.example` ឬ `.env.codex.example` ទៅ `.env` រួចដោះ comment ការកំណត់ដែលអ្នកចង់ផ្លាស់ប្តូរ។

**អាទិភាព:** Environment variables > ឯកសារ `.env` > តម្លៃ default

```ini
# AI Provider: "claude" ឬ "codex"
AI_PROVIDER=claude

# ការកំណត់ Claude
CLAUDE_MODEL=claude-sonnet-4-5-20250929
CLAUDE_MAX_TURNS=15
CLAUDE_PARALLEL=3
CLAUDE_DEBUG=0
CLAUDE_TIMEOUT=600

# ការកំណត់ Codex
# CODEX_MODEL=             # ទុកទទេ ដើម្បីប្រើ model default របស់ Codex CLI (ណែនាំ)
CODEX_SANDBOX=workspace-write
CODEX_PARALLEL=3

# ទីតាំងឯកសារ
INPUT_DIR=../1-images-to-convert
OUTPUT_DIR=../2-image-converted
PROMPT_TEMPLATE=../prompt-template.txt
```

### កំណត់ជំនួសតាម CLI

```bash
CLAUDE_MODEL=claude-opus-4-6 python3 convert.py        # គុណភាព Opus
AI_PROVIDER=codex python3 convert.py                    # ប្រើ Codex
CLAUDE_PARALLEL=5 python3 convert.py                    # ដំណើរការ 5 ក្នុងពេលតែមួយ
CLAUDE_DEBUG=1 python3 convert.py                       # បង្ហាញព័ត៌មានលម្អិត
```

## Model

| Model | ល្បឿន | គុណភាព | តម្លៃ/រូបភាព |
|-------|--------|---------|--------------|
| `claude-sonnet-4-5-20250929` | ~១ នាទី | ល្អ | ~$០.៦០ |
| `claude-opus-4-6` | ~៣ នាទី | ល្អបំផុត | ~$១.៥០ |
| `claude-haiku-4-5-20251001` | ~៣០វិ | មូលដ្ឋាន | ~$០.១០ |
| *(Codex default)* | ~២ នាទី | ល្អ | — |
| `o4-mini` (Codex) | ~១ នាទី | ល្អ | ត្រូវការគណនី API |
| `o3` (Codex) | ~២ នាទី | ខ្ពស់ជាង | ត្រូវការគណនី API |

## រចនាសម្ព័ន្ធគម្រោង

```
py/
├── convert.py              Script បម្លែងសំខាន់
├── run_claude.bat          Launcher សម្រាប់ Windows (Claude)
├── run_codex.bat           Launcher សម្រាប់ Windows (Codex)
├── .env.claude.example     គំរូកំណត់រចនាសម្ព័ន្ធ Claude (ចម្លងទៅ .env)
├── .env.codex.example      គំរូកំណត់រចនាសម្ព័ន្ធ Codex (ចម្លងទៅ .env)
├── prompt-template.txt     Prompt AI ជាមួយគំរូ SVG
├── DOCUMENT.md             ឯកសារបច្ចេកទេសពេញលេញ
├── README_KH.md            ឯកសារនេះ (ភាសាខ្មែរ)
├── config/
│   ├── __init__.py         load_config() — ផ្ទុកការកំណត់រចនាសម្ព័ន្ធ
│   ├── constants.py        តម្លៃ default, model presets, provider IDs
│   └── env_loader.py       អាន .env ដោយមិនត្រូវការ dependency បន្ថែម
├── 1-images-to-convert/    ដាក់រូបភាពបញ្ចូលនៅទីនេះ
├── 2-image-converted/      SVG ដែលបង្កើតនឹងបង្ហាញនៅទីនេះ
└── 3-image-archive/        រូបភាពដែលបម្លែងរួចត្រូវបានផ្ទេរមកទីនេះ
```

## លទ្ធផល SVG

SVG នីមួយៗមាន panel ពីរដាក់ជាប់គ្នា៖

| Panel | ខ្លឹមសារ |
|-------|----------|
| **ឆ្វេង** — Main UI | ចម្លង 1:1 នៃរូបភាពថតអេក្រង់ ជាមួយស្រទាប់ Figma ដែលមានឈ្មោះ |
| **ស្តាំ** — Variants | ស្ថានភាព Button/Dropdown (Default, Hover, Pressed, Active) |

## នាំចូលទៅ Figma

1. បើក **Figma** → File ថ្មី
2. **File** → **Place Image** (ឬអូសរួចទម្លាក់)
3. ជ្រើសរើសឯកសារ SVG ពី `2-image-converted/`
4. ស្រទាប់និង component ទាំងអស់អាចកែសម្រួលបាន

## តម្រូវការ

- **Python** 3.10+
- **AI CLI** — [Claude CLI](https://docs.anthropic.com/en/docs/claude-code) ឬ [Codex CLI](https://github.com/openai/codex)
- **មិនត្រូវការ pip dependencies** — ប្រើតែ stdlib

## ទម្រង់ឯកសារដែលគាំទ្រ

PNG, JPG, JPEG, WEBP, GIF, BMP

## ឯកសារ

សូមមើល [DOCUMENT.md](DOCUMENT.md) សម្រាប់ឯកសារបច្ចេកទេសពេញលេញ។

## ភាសា

ឯកសារនេះមានជាភាសា៖
- **English** — [README.md](README.md)
- **ខ្មែរ (Khmer)** — [README_KH.md](README_KH.md)
