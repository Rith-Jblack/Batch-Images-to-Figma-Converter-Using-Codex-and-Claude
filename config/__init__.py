"""
Configuration module for figma-converter.

Usage:
    from config import load_config
    cfg = load_config()
"""

import os
import shutil
from pathlib import Path

from .env_loader import load_dotenv
from .constants import (
    DEFAULT_PROVIDER, VALID_PROVIDERS, PROVIDER_CLAUDE, PROVIDER_CODEX,
    CLAUDE_DEFAULT_MODEL, CLAUDE_DEFAULT_MAX_TURNS,
    CLAUDE_DEFAULT_PARALLEL, CLAUDE_DEFAULT_TIMEOUT,
    CODEX_DEFAULT_MODEL, CODEX_DEFAULT_SANDBOX,
    CODEX_DEFAULT_PARALLEL, CODEX_DEFAULT_TIMEOUT,
    IMAGE_EXTENSIONS,
)


def load_config():
    """
    Load configuration from .env file + environment variables.

    Priority (highest to lowest):
      1. System environment variables
      2. .env file values
      3. Built-in defaults from constants.py

    Returns a dict with normalized keys.
    """
    script_dir = Path(__file__).resolve().parent.parent  # py/
    project_dir = script_dir.parent                       # figma-converter/

    # Load .env (does NOT override existing env vars)
    load_dotenv(script_dir / ".env")

    # Determine provider (auto-detect if not set)
    provider_env = os.environ.get("AI_PROVIDER", "").lower().strip()
    if provider_env in VALID_PROVIDERS:
        provider = provider_env
    else:
        # Auto-detect: check which CLIs are installed
        has_claude = shutil.which("claude") is not None
        has_codex = shutil.which("codex") is not None
        if has_claude:
            provider = PROVIDER_CLAUDE
        elif has_codex:
            provider = PROVIDER_CODEX
        else:
            provider = DEFAULT_PROVIDER  # will fail later with helpful error

    # Provider-specific settings with generic AI_* fallback
    if provider == PROVIDER_CODEX:
        model = os.environ.get("CODEX_MODEL",
                os.environ.get("AI_MODEL", CODEX_DEFAULT_MODEL))
        parallel = int(os.environ.get("CODEX_PARALLEL",
                   os.environ.get("AI_PARALLEL", str(CODEX_DEFAULT_PARALLEL))))
        debug = os.environ.get("CODEX_DEBUG",
                os.environ.get("AI_DEBUG", "0")) == "1"
        timeout = int(os.environ.get("CODEX_TIMEOUT",
                  os.environ.get("AI_TIMEOUT", str(CODEX_DEFAULT_TIMEOUT))))
        sandbox = os.environ.get("CODEX_SANDBOX", CODEX_DEFAULT_SANDBOX)
        max_turns = None  # Codex has no max-turns
    else:
        model = os.environ.get("CLAUDE_MODEL",
                os.environ.get("AI_MODEL", CLAUDE_DEFAULT_MODEL))
        max_turns = os.environ.get("CLAUDE_MAX_TURNS", CLAUDE_DEFAULT_MAX_TURNS)
        parallel = int(os.environ.get("CLAUDE_PARALLEL",
                   os.environ.get("AI_PARALLEL", str(CLAUDE_DEFAULT_PARALLEL))))
        debug = os.environ.get("CLAUDE_DEBUG",
                os.environ.get("AI_DEBUG", "0")) == "1"
        timeout = int(os.environ.get("CLAUDE_TIMEOUT",
                  os.environ.get("AI_TIMEOUT", str(CLAUDE_DEFAULT_TIMEOUT))))
        sandbox = None

    # Resolve CLI executable path (handles .cmd wrappers on Windows)
    cli_name = "codex" if provider == PROVIDER_CODEX else "claude"
    cli_path = shutil.which(cli_name) or cli_name

    # Paths (shared across providers)
    input_dir = Path(os.environ.get("INPUT_DIR", project_dir / "1-images-to-convert"))
    output_dir = Path(os.environ.get("OUTPUT_DIR", project_dir / "2-image-converted"))
    archive_dir = Path(os.environ.get("ARCHIVE_DIR", script_dir / "3-image-archive"))
    prompt_tpl = Path(os.environ.get("PROMPT_TEMPLATE",
                      project_dir / "prompt-template.txt"))

    return {
        "provider": provider,
        "cli_path": cli_path,
        "model": model,
        "max_turns": max_turns,
        "parallel": parallel,
        "debug": debug,
        "timeout": timeout,
        "sandbox": sandbox,
        "script_dir": script_dir,
        "project_dir": project_dir,
        "input_dir": input_dir,
        "output_dir": output_dir,
        "archive_dir": archive_dir,
        "prompt_tpl": prompt_tpl,
        "image_extensions": IMAGE_EXTENSIONS,
    }
