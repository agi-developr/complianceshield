"""
ComplianceShield Telegram Bot -- thin client over the REST API.

Setup:
  1. Open Telegram, search for @BotFather, send /newbot
  2. Follow prompts: pick a name ("ComplianceShield") and username (e.g. ComplianceShieldBot)
  3. BotFather gives you a token like 123456:ABC-DEF...
  4. Add to .env:  TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
  5. Make sure the compliance API is running:  poetry run web-demo
  6. Run the bot:  poetry run python -m src.telegram_bot

Commands:
  /start              - Welcome message
  /scan <text>        - Quick compliance scan
  /scanfull <text>    - Full analysis
  /video <url>        - Scan a YouTube video transcript
  (any plain text)    - Auto quick-scan
"""

import json
import logging
import os

import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE = os.getenv("COMPLIANCE_API_URL", "http://localhost:8080")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

RISK_EMOJI = {"HIGH": "\U0001F534", "MEDIUM": "\U0001F7E1", "LOW": "\U0001F7E2", "UNKNOWN": "\u26AA"}
CATEGORY_EMOJI = {
    "FTC": "\U0001F4DC",
    "HEALTH": "\U0001F3E5",
    "FINANCIAL": "\U0001F4B0",
    "PRIVACY": "\U0001F512",
    "DECEPTIVE": "\U0001F3AD",
}

# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

async def api_scan(content: str, detail_level: str = "quick") -> dict:
    """POST /api/scan and return the JSON response."""
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{API_BASE}/api/scan",
            json={"content": content, "detail_level": detail_level},
        )
        resp.raise_for_status()
        return resp.json()


async def api_scan_video(youtube_url: str, detail_level: str = "quick") -> dict:
    """POST /api/scan-video and return the JSON response."""
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{API_BASE}/api/scan-video",
            json={"youtube_url": youtube_url, "detail_level": detail_level},
        )
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

def _fmt_risk(level: str) -> str:
    emoji = RISK_EMOJI.get(level, "\u26AA")
    return f"{emoji} {level}"


def _fmt_category(cat: str) -> str:
    for key, em in CATEGORY_EMOJI.items():
        if key in cat.upper():
            return f"{em} {cat}"
    return f"\U0001F4CB {cat}"


def format_report(data: dict) -> str:
    """Turn the API JSON into a nice Telegram message."""
    status = data.get("status", "unknown")
    if status == "error":
        return f"\u274C *Error*: {data.get('error', 'Unknown error')}"

    report = data.get("report", {})
    risk = report.get("overall_risk", "UNKNOWN")
    issues = report.get("issues", [])
    detail = data.get("detail_level", "quick")
    elapsed = data.get("elapsed_seconds", "?")

    lines = [
        f"\U0001F6E1 *ComplianceShield Report*  ({detail})",
        f"Risk: {_fmt_risk(risk)}",
        "",
    ]

    if issues:
        lines.append(f"\u26A0\uFE0F *{len(issues)} issue(s) found:*")
        for i, issue in enumerate(issues, 1):
            sev = issue.get("severity", "?")
            cat = issue.get("category", "general")
            desc = issue.get("description", "No description")
            lines.append(f"  {i}. {_fmt_category(cat)} [{sev}]")
            lines.append(f"     {desc}")
        lines.append("")
    else:
        lines.append("\u2705 No compliance issues detected!")
        lines.append("")

    # Recommendations
    recs = report.get("recommendations", [])
    if recs:
        lines.append("\U0001F4A1 *Recommendations:*")
        for r in recs[:5]:
            lines.append(f"  \u2022 {r}")
        lines.append("")

    lines.append(f"\u23F1 Scanned in {elapsed}s")
    return "\n".join(lines)


def format_video_report(data: dict) -> str:
    """Format a video scan result."""
    base = format_report(data)
    video = data.get("video", {})
    if video:
        vid_id = video.get("video_id", "?")
        duration = video.get("duration_seconds", 0)
        mins = duration // 60
        secs = duration % 60
        base += f"\n\U0001F3AC Video: {vid_id} ({mins}m {secs}s)"
    return base


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start."""
    text = (
        "\U0001F6E1 *ComplianceShield Bot*\n\n"
        "I scan your marketing copy, ads, and video content for "
        "FTC, health, financial, and privacy compliance issues.\n\n"
        "*Commands:*\n"
        "/scan <text> \u2014 Quick compliance scan\n"
        "/scanfull <text> \u2014 Full detailed analysis\n"
        "/video <youtube\\_url> \u2014 Scan a YouTube video\n\n"
        "Or just send me any text and I'll auto-scan it!\n\n"
        "\U0001F50D Powered by AI \u2022 Not legal advice"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_scan(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /scan <text>."""
    content = " ".join(ctx.args) if ctx.args else ""
    if not content:
        await update.message.reply_text("Usage: /scan <text to check>")
        return
    await _do_scan(update, content, "quick")


async def cmd_scanfull(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /scanfull <text>."""
    content = " ".join(ctx.args) if ctx.args else ""
    if not content:
        await update.message.reply_text("Usage: /scanfull <text to check>")
        return
    await _do_scan(update, content, "full")


async def cmd_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /video <youtube_url>."""
    url = ctx.args[0] if ctx.args else ""
    if not url or "youtu" not in url:
        await update.message.reply_text(
            "Usage: /video <youtube\\_url>\n"
            "Example: /video https://www.youtube.com/watch?v=abc123",
            parse_mode="Markdown",
        )
        return

    waiting = await update.message.reply_text("\U0001F3AC Extracting transcript & scanning...")
    try:
        data = await api_scan_video(url, "full")
        msg = format_video_report(data)
    except httpx.HTTPStatusError as exc:
        msg = f"\u274C API error: {exc.response.status_code}"
    except Exception as exc:
        msg = f"\u274C Error: {exc}"

    await waiting.edit_text(msg, parse_mode="Markdown")


async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Auto quick-scan any plain text message."""
    content = update.message.text or ""
    if not content.strip():
        return
    await _do_scan(update, content, "quick")


async def _do_scan(update: Update, content: str, detail_level: str) -> None:
    """Shared scan logic: send waiting message, call API, reply with report."""
    label = {"quick": "Quick scan", "full": "Full analysis", "deep": "Deep review"}
    waiting = await update.message.reply_text(
        f"\U0001F50D {label.get(detail_level, 'Scanning')}..."
    )
    try:
        data = await api_scan(content, detail_level)
        msg = format_report(data)
    except httpx.HTTPStatusError as exc:
        msg = f"\u274C API error: {exc.response.status_code}"
    except httpx.ConnectError:
        msg = (
            "\u274C Cannot reach ComplianceShield API.\n"
            "Make sure the server is running:\n"
            "`poetry run web-demo`"
        )
    except Exception as exc:
        msg = f"\u274C Error: {exc}"

    await waiting.edit_text(msg, parse_mode="Markdown")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not BOT_TOKEN:
        print("ERROR: Set TELEGRAM_BOT_TOKEN in .env")
        print("  1. Talk to @BotFather on Telegram")
        print("  2. /newbot -> pick name & username")
        print("  3. Copy the token into .env")
        raise SystemExit(1)

    print(f"ComplianceShield Telegram Bot starting...")
    print(f"  API: {API_BASE}")
    print(f"  Mode: polling")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("scan", cmd_scan))
    app.add_handler(CommandHandler("scanfull", cmd_scanfull))
    app.add_handler(CommandHandler("video", cmd_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("  Bot is live! Press Ctrl+C to stop.\n")
    app.run_polling()


if __name__ == "__main__":
    main()
