"""
Image to Figma Professional Design Converter
Uses Claude CLI or OpenAI Codex CLI to analyze UI screenshots and generate
Figma-ready SVGs with component variants and interaction annotations.
"""

import os
import sys
import time
import subprocess
import tempfile
import math
import json
import shutil
import concurrent.futures
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# -- Configuration (loaded from .env + env vars + defaults) --------------------

from config import load_config
from config.constants import (
    PROVIDER_CLAUDE, PROVIDER_CODEX,
    PLACEHOLDER_IMAGE, PLACEHOLDER_OUTPUT,
    TIME_ESTIMATES, DEFAULT_TIME_ESTIMATE,
)

# Allow running from within another Claude session
os.environ.pop("CLAUDECODE", None)


# -- Colors (ANSI) ------------------------------------------------------------

class C:
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[93m"
    RED = "\033[31m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def colorize(text, color):
    return f"{color}{text}{C.RESET}"


# -- Progress bar --------------------------------------------------------------

def progress_bar(current, total, width=40):
    pct = int(current * 100 / total)
    filled = int(pct / 100 * width)
    empty = width - filled
    bar = "=" * filled + "-" * empty
    return f"[{bar}] {pct}%"


def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.0f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m {s}s"


def format_tokens(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def status(msg):
    print(f"    {colorize('→', C.CYAN)} {msg}")


# -- Provider: command building ------------------------------------------------

def build_claude_command(prompt, img, cfg):
    """Build the subprocess command list for Claude CLI."""
    return [
        cfg["cli_path"], "-p", prompt,
        "--allowedTools", "Read,Write,Edit",
        "--max-turns", cfg["max_turns"],
        "--model", cfg["model"],
        "--output-format", "json",
    ]


def build_codex_command(prompt, img, cfg):
    """Build the subprocess command list for Codex CLI.

    Returns (cmd_list, stdin_text).  The prompt is passed via stdin
    (using '-') because it can exceed the OS command-line length limit.
    """
    cmd = [
        cfg["cli_path"], "exec",
        "--full-auto",
        "--sandbox", cfg["sandbox"],
        "--json",
        "--image", str(img),
    ]
    if cfg["model"]:
        cmd.extend(["--model", cfg["model"]])
    cmd.append("-")  # read prompt from stdin
    return cmd


def build_command(prompt, img, cfg):
    """Dispatch to the correct provider's command builder."""
    if cfg["provider"] == PROVIDER_CODEX:
        return build_codex_command(prompt, img, cfg)
    return build_claude_command(prompt, img, cfg)


# -- Provider: prompt adaptation -----------------------------------------------

def adapt_prompt(prompt_template, img, output_svg, cfg):
    """
    Adapt the prompt template for the current provider.

    Claude: Replace __IMAGE_PATH__ (Claude reads the file via its Read tool).
    Codex:  Remove "Read: __IMAGE_PATH__" since Codex gets the image via --image flag.
    """
    prompt = prompt_template.replace(PLACEHOLDER_OUTPUT, str(output_svg))

    if cfg["provider"] == PROVIDER_CODEX:
        # Codex receives the image via --image flag
        prompt = prompt.replace(
            f"Read: {PLACEHOLDER_IMAGE}",
            "The image is attached to this message (via --image flag)."
        )
        prompt = prompt.replace(PLACEHOLDER_IMAGE, str(img))
    else:
        prompt = prompt.replace(PLACEHOLDER_IMAGE, str(img))

    return prompt


# -- Provider: token/cost parsing ----------------------------------------------

def parse_claude_tokens(stdout):
    """Parse Claude CLI JSON output for token usage and cost."""
    try:
        data = json.loads(stdout)
        usage = data.get("usage", {})
        input_tok = usage.get("input_tokens", 0)
        cache_create = usage.get("cache_creation_input_tokens", 0)
        cache_read = usage.get("cache_read_input_tokens", 0)
        output_tok = usage.get("output_tokens", 0)
        cost_usd = data.get("total_cost_usd", 0.0)
        return {
            "input": input_tok + cache_create + cache_read,
            "output": output_tok,
            "total": input_tok + cache_create + cache_read + output_tok,
            "cost_usd": cost_usd,
        }
    except (json.JSONDecodeError, TypeError, AttributeError):
        return {"input": 0, "output": 0, "total": 0, "cost_usd": 0.0}


def parse_codex_tokens(stdout):
    """
    Parse Codex CLI JSONL output for token usage.

    Codex streams newline-delimited JSON events. We sum usage from
    events that contain token data. Codex does not report cost_usd.
    """
    total_input = 0
    total_output = 0

    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        usage = event.get("usage", {})
        if usage:
            total_input += usage.get("input_tokens", 0)
            total_input += usage.get("cached_input_tokens", 0)
            total_output += usage.get("output_tokens", 0)

    return {
        "input": total_input,
        "output": total_output,
        "total": total_input + total_output,
        "cost_usd": 0.0,
    }


def parse_token_usage(stdout, provider):
    """Dispatch to the correct provider's token parser."""
    if provider == PROVIDER_CODEX:
        return parse_codex_tokens(stdout)
    return parse_claude_tokens(stdout)


# -- Time estimation -----------------------------------------------------------

def estimate_time_per_image(model_name):
    """Return estimated minutes per image based on model name substring."""
    model_lower = model_name.lower()
    for key, minutes in TIME_ESTIMATES.items():
        if key in model_lower:
            return minutes
    return DEFAULT_TIME_ESTIMATE


# -- Single image conversion (thread-safe) ------------------------------------

def convert_image(img, prompt_template, cfg):
    """Convert a single image. Returns (filename, success, elapsed, size_kb, error, tokens)."""
    filename = img.name
    name = img.stem
    output_svg = cfg["output_dir"] / f"{name}.svg"
    tokens = {"input": 0, "output": 0, "total": 0, "cost_usd": 0.0}
    provider = cfg["provider"]

    img_start = time.time()

    # Build prompt (provider-specific adaptation)
    prompt = adapt_prompt(prompt_template, img, output_svg, cfg)

    # Write prompt to temp file (for debugging reference)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(prompt)
        prompt_file = f.name

    try:
        cmd = build_command(prompt, img, cfg)

        if cfg["debug"]:
            display_cmd = " ".join(c if c != prompt else "[prompt]" for c in cmd)
            print(f"    {C.DIM}CMD: {display_cmd}{C.RESET}")

        # Codex receives the prompt via stdin; Claude via -p flag
        stdin_text = prompt if provider == PROVIDER_CODEX else None

        result = subprocess.run(
            cmd,
            input=stdin_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=cfg["timeout"],
        )

        tokens = parse_token_usage(result.stdout, provider)

        if cfg["debug"] and result.stdout:
            print(f"    {C.DIM}{provider} output ({filename}, first 500 chars): {result.stdout[:500]}{C.RESET}")
        if cfg["debug"] and result.stderr:
            print(f"    {C.DIM}{provider} stderr ({filename}): {result.stderr[:300]}{C.RESET}")

        # Surface errors from the CLI (e.g. model not supported)
        if result.returncode != 0:
            error_msg = ""
            if result.stderr:
                error_msg = result.stderr.strip()[:200]
            # Codex streams errors as JSONL on stdout
            if not error_msg and result.stdout:
                for line in result.stdout.splitlines():
                    try:
                        ev = json.loads(line)
                        if ev.get("type") == "error":
                            error_msg = ev.get("message", "")[:200]
                            break
                    except (json.JSONDecodeError, AttributeError):
                        pass
            if error_msg:
                elapsed = time.time() - img_start
                return (filename, False, elapsed, 0, error_msg, tokens)

    except subprocess.TimeoutExpired:
        elapsed = time.time() - img_start
        return (filename, False, elapsed, 0, "timeout", tokens)
    except FileNotFoundError:
        elapsed = time.time() - img_start
        return (filename, False, elapsed, 0, "cli_not_found", tokens)
    except Exception as exc:
        elapsed = time.time() - img_start
        return (filename, False, elapsed, 0, str(exc)[:200], tokens)
    finally:
        try:
            os.unlink(prompt_file)
        except OSError:
            pass

    elapsed = time.time() - img_start

    if output_svg.exists() and output_svg.stat().st_size > 0:
        size_kb = output_svg.stat().st_size // 1024
        return (filename, True, elapsed, size_kb, None, tokens)
    else:
        return (filename, False, elapsed, 0, None, tokens)


# -- Main ----------------------------------------------------------------------

def main():
    # Enable ANSI on Windows
    if sys.platform == "win32":
        os.system("")

    # Load configuration from .env + env vars + defaults
    cfg = load_config()

    # Header
    print()
    print(colorize("  +=====================================================+", C.MAGENTA))
    print(colorize("  |                                                     |", C.MAGENTA))
    print(colorize("  |     Image -> Figma Design Converter                 |", C.MAGENTA))
    print(colorize("  |     Professional Component Generator   (Python)     |", C.MAGENTA))
    print(colorize("  |                                                     |", C.MAGENTA))
    print(colorize("  +=====================================================+", C.MAGENTA))
    print()

    # Validate prompt template
    if not cfg["prompt_tpl"].exists():
        print(colorize("  [ERROR] Missing prompt-template.txt", C.RED))
        print(f"    {cfg['prompt_tpl']}")
        input("\n  Press Enter to exit...")
        sys.exit(1)

    prompt_template = cfg["prompt_tpl"].read_text(encoding="utf-8")

    # Setup output dir and archive dir
    cfg["output_dir"].mkdir(parents=True, exist_ok=True)
    cfg["archive_dir"].mkdir(parents=True, exist_ok=True)

    # Collect images
    images = []
    for ext in cfg["image_extensions"]:
        images.extend(cfg["input_dir"].glob(ext))
        # Also check uppercase
        images.extend(cfg["input_dir"].glob(ext.upper()))
    # Deduplicate (case-insensitive glob on Windows may return same files)
    seen = set()
    unique_images = []
    for img in images:
        key = str(img).lower()
        if key not in seen:
            seen.add(key)
            unique_images.append(img)
    images = sorted(unique_images, key=lambda p: p.name)

    total = len(images)

    if total == 0:
        print(colorize("  [ERROR] No images found in:", C.RED))
        print(f"    {colorize(str(cfg['input_dir']), C.DIM)}")
        print()
        print(f"  {colorize('Supported: PNG, JPG, JPEG, WEBP, GIF, BMP', C.DIM)}")
        input("\n  Press Enter to exit...")
        sys.exit(1)

    # Display config
    provider_label = cfg["provider"].upper()
    print(f"  {colorize('Provider:', C.CYAN)} {colorize(provider_label, C.BOLD)}")
    print(f"  {colorize('Source:', C.CYAN)}   {cfg['input_dir']}")
    print(f"  {colorize('Output:', C.CYAN)}   {cfg['output_dir']}")
    print(f"  {colorize('Archive:', C.CYAN)}  {cfg['archive_dir']}")
    print(f"  {colorize('Model:', C.CYAN)}    {colorize(cfg['model'] or '(default)', C.BOLD)}")
    if cfg["max_turns"] is not None:
        print(f"  {colorize('Turns:', C.CYAN)}    {cfg['max_turns']}")
    print(f"  {colorize('Images:', C.CYAN)}   {colorize(str(total), C.BOLD)} file(s) found")
    print(f"  {colorize('Parallel:', C.CYAN)} {colorize(str(cfg['parallel']), C.BOLD)} concurrent")

    # Estimate time based on model
    est_per_image = estimate_time_per_image(cfg["model"])
    est_batches = math.ceil(total / cfg["parallel"])
    est_total = est_batches * est_per_image
    print(f"  {colorize('Est:', C.CYAN)}      ~{format_time(est_total * 60)}")
    print(f"  {colorize('Token:', C.CYAN)}    {colorize('live token tracking enabled', C.DIM)}")

    print()
    print(f"  {colorize('----------------------------------------------------', C.DIM)}")
    print()

    success_count = 0
    fail_count = 0
    failed_files = []
    total_tokens = 0
    total_cost = 0.0
    start_time = time.time()

    # -- Show queued images ----------------------------------------------------
    for i, img in enumerate(images):
        print(f"  {colorize(f'  [{i+1}]', C.DIM)} {img.name}")
    print()

    # -- Parallel conversion ---------------------------------------------------
    completed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=cfg["parallel"]) as executor:
        futures = {}
        for img in images:
            future = executor.submit(convert_image, img, prompt_template, cfg)
            futures[future] = img

        for future in concurrent.futures.as_completed(futures):
            completed += 1
            filename, success, elapsed, size_kb, error, tokens = future.result()

            if error == "cli_not_found":
                cli_name = "claude" if cfg["provider"] == PROVIDER_CLAUDE else "codex"
                print(colorize(f"    Error: '{cli_name}' CLI not found. Make sure it's installed and in PATH.", C.RED))
                input("\n  Press Enter to exit...")
                sys.exit(1)

            if error and error not in ("cli_not_found",):
                print(f"    {colorize('Error:', C.RED)} {error}")

            # Accumulate token usage
            total_tokens += tokens["total"]
            total_cost += tokens["cost_usd"]

            time_str = format_time(elapsed)
            name = Path(filename).stem
            bar = progress_bar(completed, total)
            tok_str = f"{format_tokens(tokens['total'])} tok"
            cost_str = f"${tokens['cost_usd']:.4f}"

            if success:
                success_count += 1
                # Move source image to archive
                src_img = futures[future]
                try:
                    shutil.move(str(src_img), str(cfg["archive_dir"] / src_img.name))
                except Exception:
                    pass  # non-critical; image stays in input
                print(f"  {colorize(bar, C.CYAN)}  {colorize('[OK]', C.GREEN)} {name}.svg ({size_kb}KB, {time_str}, {tok_str}, {cost_str})")
            else:
                fail_count += 1
                failed_files.append(filename)
                print(f"  {colorize(bar, C.CYAN)}  {colorize('[FAIL]', C.RED)} {filename} ({time_str})")

            # Live running total
            print(f"  {colorize(f'  Token: {format_tokens(total_tokens)} total | Cost: ${total_cost:.4f}', C.DIM)}")

    print()

    # -- Summary ---------------------------------------------------------------
    total_elapsed = time.time() - start_time
    total_time_str = format_time(total_elapsed)

    print(f"  {colorize('----------------------------------------------------', C.DIM)}")
    print()

    if fail_count == 0:
        print(colorize("  +=====================================================+", C.GREEN))
        print(colorize("  |                                                     |", C.GREEN))
        print(colorize("  |   ALL IMAGES CONVERTED SUCCESSFULLY!                |", C.GREEN))
        print(colorize("  |                                                     |", C.GREEN))
        print(colorize("  +=====================================================+", C.GREEN))
    else:
        print(colorize("  +=====================================================+", C.YELLOW))
        print(colorize("  |   CONVERSION COMPLETE WITH ERRORS                   |", C.YELLOW))
        print(colorize("  +=====================================================+", C.YELLOW))

    print()
    print(f"  {colorize('Results:', C.BOLD)}")
    print(f"    Total images:   {total}")
    print(f"    {colorize(f'Converted:      {success_count}', C.GREEN)}")
    if fail_count > 0:
        print(f"    {colorize(f'Failed:         {fail_count}', C.RED)}")
    print(f"    {colorize(f'Total time:     {total_time_str}', C.DIM)}")
    print(f"    {colorize(f'Total tokens:   {format_tokens(total_tokens)}', C.DIM)}")
    print(f"    {colorize(f'Total cost:     ${total_cost:.4f}', C.DIM)}")
    print()

    if fail_count > 0:
        print(colorize("  Failed files:", C.RED))
        for f in failed_files:
            print(f"    {colorize('X', C.RED)} {f}")
        print()

    print(colorize("  Import into Figma:", C.CYAN))
    print(f"    {colorize('1.', C.CYAN)} Open Figma > New File")
    print(f"    {colorize('2.', C.CYAN)} File > Place Image (or drag and drop)")
    print(f"    {colorize('3.', C.CYAN)} Select SVG files from:")
    print(f"       {colorize(str(cfg['output_dir']), C.BOLD)}")
    print(f"    {colorize('4.', C.CYAN)} All layers and components will be editable")
    print()
    print(f"  {colorize('SVG layers named with Figma conventions', C.DIM)}")
    print(f"  {colorize('Component variants included (Hover/Active/Disabled/Focus)', C.DIM)}")
    print(f"  {colorize('Prototyping interactions annotated via data-* attributes', C.DIM)}")
    print()

    input("  Press Enter to exit...")


if __name__ == "__main__":
    main()
