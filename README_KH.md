# Image to Figma Converter (Python)

បម្លែងរូបភាពថតអេក្រង់ UI ទៅជា **ឯកសារ SVG សម្រាប់ Figma** ដែលមានស្រទាប់ដែលមានឈ្មោះ, វ៉ារ្យ៉ង់សមាសភាគ, និងចំណាំបង្កើតគំរូ — ដំណើរការដោយ Claude AI ឬ OpenAI Codex។

```
រូបភាពថតអេក្រង់ (PNG/JPG) → ការវិភាគ AI → SVG ជាមួយស្រទាប់ Figma + វ៉ារ្យ៉ង់សមាសភាគ
```

## ចាប់ផ្តើមរហ័ស

```bash
# 1. ដាក់រូបភាពថតអេក្រង់ទៅក្នុងថតឯកសារបញ្ចូល
cp ~/screenshots/*.png ../1-images-to-convert/

# 2. (ជម្រើស) កំណត់រចនាសម្ព័ន្ធតាមរយៈ .env
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

ចម្លង `.env.claude.example` ឬ `.env.codex.example` ទៅ `.env` ហើយបើកការកំណត់ដែលអ្នកចង់ផ្លាស់ប្តូរ។

**អាទិភាព:** អថេរបរិស្ថាន > ឯកសារ `.env` > តម្លៃលំនាំដើម

```ini
# ក្រុមហ៊ុនផ្តល់ AI: "claude" ឬ "codex"
AI_PROVIDER=claude

# ការកំណត់ Claude
CLAUDE_MODEL=claude-sonnet-4-5-20250929
CLAUDE_MAX_TURNS=15
CLAUDE_PARALLEL=3
CLAUDE_DEBUG=0
CLAUDE_TIMEOUT=600

# ការកំណត់ Codex
CODEX_MODEL=o4-mini
CODEX_SANDBOX=workspace-write
CODEX_PARALLEL=3

# ផ្លូវឯកសារ
INPUT_DIR=../1-images-to-convert
OUTPUT_DIR=../2-image-converted
PROMPT_TEMPLATE=../prompt-template.txt
```

### បដិសេធតាមរយៈ CLI

```bash
CLAUDE_MODEL=claude-opus-4-6 python3 convert.py        # គុណភាព Opus
AI_PROVIDER=codex python3 convert.py                    # ប្រើ Codex
CLAUDE_PARALLEL=5 python3 convert.py                    # ដំណើរការ 5 ក្នុងពេលតែមួយ
CLAUDE_DEBUG=1 python3 convert.py                       # បង្ហាញលម្អិត
```

## ម៉ូដែល

| ម៉ូដែល                          | ល្បឿន     | គុណភាព | តម្លៃ/រូបភាព |
|---------                       |--------   | ---------|--------------|
| `claude-sonnet-4-5-20250929`   | ~១ នាទី   | ល្អ | ~$០.៦០ |
| `claude-opus-4-6` | ~៣ នាទី    | ល្អបំផុត   | ~$១.៥០ |
| `claude-haiku-4-5-20251001`    | ~៣០វិ     | មូលដ្ឋាន | ~$០.១០ |
| `o4-mini` (Codex) | ~១ នាទី    | ល្អ        | — |
| `o3` (Codex) | ~២ នាទី         | ខ្ពស់ជាង   | — |

## រចនាសម្ព័ន្ធគម្រោង

```
py/
├── convert.py              ស្គ្រីបបម្លែងសំខាន់
├── run_claude.bat          កម្មវិធីបើកដំណើរការ Windows (Claude)
├── run_codex.bat           កម្មវិធីបើកដំណើរការ Windows (Codex)
├── .env.claude.example     គំរូកំណត់រចនាសម្ព័ន្ធ Claude (ចម្លងទៅ .env)
├── .env.codex.example      គំរូកំណត់រចនាសម្ព័ន្ធ Codex (ចម្លងទៅ .env)
├── prompt-template.txt     ពាក្យបញ្ជា AI ជាមួយគំរូ SVG
├── DOCUMENT.md             ឯកសារបច្ចេកទេសពេញលេញ
├── README_KH.md            ឯកសារនេះ (ភាសាខ្មែរ)
├── config/
│   ├── __init__.py         load_config() — កម្មវិធីផ្ទុកការកំណត់រចនាសម្ព័ន្ធ
│   ├── constants.py        តម្លៃលំនាំដើម, គំរូម៉ូដែល, អត្តសញ្ញាណក្រុមហ៊ុនផ្តល់
│   └── env_loader.py       កម្មវិធីអាន .env មិនត្រូវការកម្មវិធីបន្ថែម
├── 1-images-to-convert/    ដាក់រូបភាពបញ្ចូលនៅទីនេះ
├── 2-image-converted/      ឯកសារ SVG ដែលបានបង្កើតនឹងបង្ហាញនៅទីនេះ
└── 3-image-archive/        រូបភាពដែលបានបម្លែងត្រូវបានរក្សាទុកនៅទីនេះ
```

## លទ្ធផល SVG

SVG នីមួយៗមានផ្ទាំងពីរដាក់ជាប់គ្នា៖

| ផ្ទាំង | ខ្លឹមសារ |
|--------|----------|
| **ឆ្វេង** — UI សំខាន់ | ចម្លង 1:1 នៃរូបភាពថតអេក្រង់ជាមួយស្រទាប់ Figma ដែលមានឈ្មោះ |
| **ស្តាំ** — វ៉ារ្យ៉ង់ | ស្ថានភាពប៊ូតុង/ម៉ឺនុយទម្លាក់ (លំនាំដើម, Hover, Pressed, Active) |

## ការនាំចូលទៅ Figma

1. បើក **Figma** → ឯកសារថ្មី
2. **File** → **Place Image** (ឬអូសហើយទម្លាក់)
3. ជ្រើសរើសឯកសារ SVG ពី `2-image-converted/`
4. ស្រទាប់និងសមាសភាគទាំងអស់អាចកែសម្រួលបាន

## តម្រូវការ

- **Python** 3.10+
- **AI CLI** — [Claude CLI](https://docs.anthropic.com/en/docs/claude-code) ឬ [Codex CLI](https://github.com/openai/codex)
- **មិនត្រូវការ pip dependencies** — ប្រើតែ stdlib

## ទម្រង់ឯកសារដែលគាំទ្រ

PNG, JPG, JPEG, WEBP, GIF, BMP

## ឯកសារ

សូមមើល [DOCUMENT.md](DOCUMENT.md) សម្រាប់ឯកសារបច្ចេកទេសពេញលេញ។

---

> **ភាសា / Languages:** [English](README.md) | **ខ្មែរ (Khmer)**
