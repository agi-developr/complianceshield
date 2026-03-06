"""
Strands agent definition with Nevermined x402 payment-protected compliance tools.

Usage:
    from src.strands_agent import payments, create_agent, NVM_PLAN_ID
"""

import os

from dotenv import load_dotenv
from strands import Agent, tool

from payments_py import Payments, PaymentOptions
from payments_py.x402.strands import requires_payment

from .tools.compliance_check import quick_scan_impl, full_analysis_impl, deep_review_impl
from .tools.youtube_transcript import get_transcript_impl

load_dotenv()

NVM_API_KEY = os.environ["NVM_API_KEY"]
NVM_ENVIRONMENT = os.getenv("NVM_ENVIRONMENT", "sandbox")
NVM_PLAN_ID = os.environ["NVM_PLAN_ID"]
NVM_AGENT_ID = os.getenv("NVM_AGENT_ID")

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
)


# ---------------------------------------------------------------------------
# Payment-protected Strands tools
# ---------------------------------------------------------------------------

@tool(context=True)
@requires_payment(
    payments=payments,
    plan_id=NVM_PLAN_ID,
    credits=1,
    agent_id=NVM_AGENT_ID,
)
def quick_scan(content: str, tool_context=None) -> dict:
    """Quick compliance scan of content. Costs 1 credit.

    Flags obvious legal issues: undisclosed sponsorships, health claims,
    financial advice, privacy concerns.

    Args:
        content: The text content (script, transcript, post) to scan.
    """
    return quick_scan_impl(content)


@tool(context=True)
@requires_payment(
    payments=payments,
    plan_id=NVM_PLAN_ID,
    credits=5,
    agent_id=NVM_AGENT_ID,
)
def full_analysis(content: str, focus: str = "all", tool_context=None) -> dict:
    """Full compliance analysis of content. Costs 5 credits.

    Detailed per-section compliance report with risk scores for each category.

    Args:
        content: The text content to analyze.
        focus: Focus area - 'all', 'health', 'financial', 'ftc', 'privacy'.
    """
    return full_analysis_impl(content, focus)


@tool(context=True)
@requires_payment(
    payments=payments,
    plan_id=NVM_PLAN_ID,
    credits=10,
    agent_id=NVM_AGENT_ID,
)
def deep_review(content: str, tool_context=None) -> dict:
    """Deep compliance review with legal citations. Costs 10 credits.

    Comprehensive analysis with specific law citations, compliant rewrites,
    and potential penalty estimates.

    Args:
        content: The text content to deeply review.
    """
    return deep_review_impl(content)


@tool(context=True)
@requires_payment(
    payments=payments,
    plan_id=NVM_PLAN_ID,
    credits=8,
    agent_id=NVM_AGENT_ID,
)
def scan_video(youtube_url: str, detail_level: str = "full", tool_context=None) -> dict:
    """Scan a YouTube video for compliance issues. Costs 8 credits.

    Extracts the video transcript and runs a compliance analysis on it.

    Args:
        youtube_url: YouTube video URL or video ID.
        detail_level: 'quick', 'full', or 'deep' analysis depth.
    """
    transcript_result = get_transcript_impl(youtube_url)
    if transcript_result["status"] == "error":
        return transcript_result

    transcript = transcript_result["transcript"]
    video_id = transcript_result["video_id"]
    duration = transcript_result["duration_seconds"]

    if detail_level == "quick":
        report = quick_scan_impl(transcript)
    elif detail_level == "deep":
        report = deep_review_impl(transcript)
    else:
        report = full_analysis_impl(transcript)

    if report.get("status") == "success":
        header = (
            f"📹 Video Compliance Report\n"
            f"Video: https://youtube.com/watch?v={video_id}\n"
            f"Duration: {duration // 60}m {duration % 60}s\n"
            f"Transcript length: {len(transcript)} chars\n\n"
        )
        report["content"] = [{"text": header + report["content"][0]["text"]}]
        report["video_id"] = video_id

    return report


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a compliance checker agent for content creators (YouTubers, TikTokers, podcasters).
You analyze content for legal and regulatory compliance issues.

You provide these services:

1. **quick_scan** (1 credit) - Quick scan for obvious compliance issues in text.
2. **full_analysis** (5 credits) - Detailed compliance analysis with risk scores.
3. **deep_review** (10 credits) - Comprehensive review with legal citations.
4. **scan_video** (8 credits) - Extract YouTube video transcript and run compliance analysis.

When given a YouTube URL, use scan_video. When given text content, choose the appropriate
text analysis tool based on complexity. Always explain findings clearly and recommend actions."""

TOOLS = [quick_scan, full_analysis, deep_review, scan_video]


def create_agent(model) -> Agent:
    """Create a Strands agent with payment-protected compliance tools."""
    return Agent(
        model=model,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )
