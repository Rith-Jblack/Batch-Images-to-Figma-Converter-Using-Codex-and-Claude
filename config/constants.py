"""
Constants and default configuration values for the figma-converter.
"""

# -- Supported image file extensions ------------------------------------------
IMAGE_EXTENSIONS = ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif", "*.bmp")

# -- AI Provider identifiers --------------------------------------------------
PROVIDER_CLAUDE = "claude"
PROVIDER_CODEX = "codex"
VALID_PROVIDERS = (PROVIDER_CLAUDE, PROVIDER_CODEX)
DEFAULT_PROVIDER = PROVIDER_CLAUDE

# -- Claude CLI defaults ------------------------------------------------------
CLAUDE_DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
CLAUDE_DEFAULT_MAX_TURNS = "15"
CLAUDE_DEFAULT_PARALLEL = 3
CLAUDE_DEFAULT_TIMEOUT = 600  # seconds

# -- Codex CLI defaults -------------------------------------------------------
CODEX_DEFAULT_MODEL = ""  # empty = let Codex CLI use its own default
CODEX_DEFAULT_SANDBOX = "workspace-write"
CODEX_DEFAULT_PARALLEL = 3
CODEX_DEFAULT_TIMEOUT = 600  # seconds

# -- Time estimation per image (minutes) --------------------------------------
# Used for display only. Keyed by substring match on model name.
TIME_ESTIMATES = {
    "haiku": 0.5,     # ~30s per image
    "opus": 3.0,      # ~3min per image
    "sonnet": 1.0,    # ~1min per image
    "o4-mini": 1.0,   # ~1min per image
    "o3": 2.0,        # ~2min per image
    "gpt": 1.5,       # ~1.5min per image
}
DEFAULT_TIME_ESTIMATE = 1.0  # fallback minutes

# -- Prompt template placeholders ---------------------------------------------
PLACEHOLDER_IMAGE = "__IMAGE_PATH__"
PLACEHOLDER_OUTPUT = "__OUTPUT_PATH__"
