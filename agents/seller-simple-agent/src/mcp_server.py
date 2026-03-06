"""MCP server exposing compliance tools with Nevermined payments.

Any MCP client (Claude Desktop, OpenClaw, Cursor, etc.) can connect
and use paid compliance checking tools.

Credit pricing:
  - quick_scan:    1 credit
  - full_analysis: 5 credits
  - deep_review:   10 credits
  - scan_video:    8 credits

Usage:
    poetry run python -m src.mcp_server
"""

import asyncio
import os
import signal

from dotenv import load_dotenv
from payments_py import Payments, PaymentOptions
from payments_py.mcp import PaymentsMCP

from .tools.compliance_check import quick_scan_impl, full_analysis_impl, deep_review_impl
from .tools.youtube_transcript import get_transcript_impl

load_dotenv()

NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
NVM_AGENT_ID = os.environ.get("NVM_AGENT_ID", "")
PORT = int(os.environ.get("MCP_PORT", os.environ.get("PORT", "3000")))

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
)

mcp = PaymentsMCP(
    payments,
    name="compliance-mcp-server",
    agent_id=NVM_AGENT_ID,
    version="1.0.0",
    description="Legal compliance checker for content creators — MCP server with Nevermined payments",
)


# --- Tools ---

@mcp.tool(credits=1)
def quick_scan(content: str) -> str:
    """Quick compliance scan for obvious legal issues in content (1 credit).

    Flags undisclosed sponsorships, health claims, financial advice, privacy concerns.

    :param content: Text content (script, transcript, social post) to scan.
    """
    result = quick_scan_impl(content)
    return result["content"][0]["text"]


@mcp.tool(credits=5)
def full_analysis(content: str, focus: str = "all") -> str:
    """Full compliance analysis with per-section risk scores (5 credits).

    Detailed report covering FTC, health/medical, financial, privacy, copyright,
    and platform policy compliance.

    :param content: Text content to analyze.
    :param focus: Focus area - 'all', 'health', 'financial', 'ftc', 'privacy'.
    """
    result = full_analysis_impl(content, focus)
    return result["content"][0]["text"]


@mcp.tool(credits=10)
def deep_review(content: str) -> str:
    """Deep compliance review with legal citations and rewrite suggestions (10 credits).

    Comprehensive analysis with specific law citations (FTC Act Section 5, etc.),
    compliant text rewrites, and penalty estimates.

    :param content: Text content to deeply review.
    """
    result = deep_review_impl(content)
    return result["content"][0]["text"]


@mcp.tool(credits=8)
def scan_video(youtube_url: str, detail_level: str = "full") -> str:
    """Scan a YouTube video for compliance issues (8 credits).

    Extracts the transcript from a YouTube video and runs compliance analysis.

    :param youtube_url: YouTube video URL or video ID.
    :param detail_level: Analysis depth - 'quick', 'full', or 'deep'.
    """
    transcript_result = get_transcript_impl(youtube_url)
    if transcript_result["status"] == "error":
        return transcript_result["content"][0]["text"]

    transcript = transcript_result["transcript"]
    video_id = transcript_result["video_id"]
    duration = transcript_result["duration_seconds"]

    if detail_level == "quick":
        report = quick_scan_impl(transcript)
    elif detail_level == "deep":
        report = deep_review_impl(transcript)
    else:
        report = full_analysis_impl(transcript)

    header = (
        f"Video Compliance Report\n"
        f"Video: https://youtube.com/watch?v={video_id}\n"
        f"Duration: {duration // 60}m {duration % 60}s\n"
        f"Transcript: {len(transcript)} chars\n\n"
    )
    return header + report["content"][0]["text"]


# --- Entry point ---

async def _run():
    result = await mcp.start(port=PORT)
    info = result["info"]
    stop = result["stop"]

    print(f"\nCompliance MCP Server running at: {info['baseUrl']}")
    print(f"  MCP endpoint:  {info['baseUrl']}/mcp")
    print(f"  Health check:  {info['baseUrl']}/health")
    print(f"  Tools: {', '.join(info.get('tools', []))}")
    print(f"  Agent ID: {NVM_AGENT_ID[:16]}..." if NVM_AGENT_ID else "  Agent ID: (none)")
    print()
    print("Connect from Claude Desktop, OpenClaw, or any MCP client.")
    print()

    loop = asyncio.get_running_loop()
    shutdown = loop.create_future()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: shutdown.set_result(True))

    await shutdown
    await stop()
    print("Server stopped.")


def main():
    asyncio.run(_run())


if __name__ == "__main__":
    main()
