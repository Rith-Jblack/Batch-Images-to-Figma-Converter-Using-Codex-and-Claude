"""
Zero-dependency .env file parser.

Reads KEY=VALUE pairs from a .env file. Lines starting with # are comments.
Existing environment variables always take precedence over .env values.
"""

import os
from pathlib import Path


def load_dotenv(filepath=None, override=False):
    """
    Parse a .env file and inject values into os.environ.

    Args:
        filepath: Path to .env file. Defaults to py/.env.
        override: If True, .env values overwrite existing env vars.
                  If False (default), existing env vars take precedence.

    Returns:
        Dict of all key-value pairs found in the .env file.
    """
    if filepath is None:
        filepath = Path(__file__).resolve().parent.parent / ".env"
    else:
        filepath = Path(filepath)

    parsed = {}

    if not filepath.exists():
        return parsed

    with open(filepath, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Must contain '='
            if "=" not in line:
                continue

            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()

            # Skip invalid keys
            if not key or " " in key:
                continue

            # Strip matching surrounding quotes
            if len(value) >= 2:
                if (value[0] == '"' and value[-1] == '"') or \
                   (value[0] == "'" and value[-1] == "'"):
                    value = value[1:-1]

            parsed[key] = value

            # Inject into os.environ (system env vars win by default)
            if override or key not in os.environ:
                os.environ[key] = value

    return parsed
