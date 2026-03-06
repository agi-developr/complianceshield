"""
Plain Strands tools WITHOUT @requires_payment — for A2A mode.

In A2A mode, payment validation and credit settlement happen at the A2A
message level via PaymentsRequestHandler.

Usage:
    from src.strands_agent_plain import create_plain_agent, CREDIT_MAP, resolve_tools
"""

from a2a.types import AgentSkill
from strands import Agent, tool

from .tools.compliance_check import quick_scan_impl, full_analysis_impl, deep_review_impl
from .tools.youtube_transcript import get_transcript_impl


# ---------------------------------------------------------------------------
# Plain Strands tools (no payment decorator)
# ---------------------------------------------------------------------------

@tool
def quick_scan(content: str) -> dict:
    """Quick compliance scan of content. Costs 1 credit.

    Flags obvious legal issues: undisclosed sponsorships, health claims,
    financial advice, privacy concerns.

    Args:
        content: The text content (script, transcript, post) to scan.
    """
    return quick_scan_impl(content)


@tool
def full_analysis(content: str, focus: str = "all") -> dict:
    """Full compliance analysis of content. Costs 5 credits.

    Detailed per-section compliance report with risk scores for each category.

    Args:
        content: The text content to analyze.
        focus: Focus area - 'all', 'health', 'financial', 'ftc', 'privacy'.
    """
    return full_analysis_impl(content, focus)


@tool
def deep_review(content: str) -> dict:
    """Deep compliance review with legal citations. Costs 10 credits.

    Comprehensive analysis with specific law citations, compliant rewrites,
    and potential penalty estimates.

    Args:
        content: The text content to deeply review.
    """
    return deep_review_impl(content)


@tool
def scan_video(youtube_url: str, detail_level: str = "full") -> dict:
    """Scan a YouTube video for compliance issues. Costs 8 credits.

    Extracts the video transcript and runs a compliance analysis on it.
    Catches FTC violations, health claims, financial advice issues, and more.

    Args:
        youtube_url: YouTube video URL or video ID.
        detail_level: 'quick', 'full', or 'deep' analysis depth.
    """
    # Step 1: Extract transcript
    transcript_result = get_transcript_impl(youtube_url)
    if transcript_result["status"] == "error":
        return transcript_result

    transcript = transcript_result["transcript"]
    video_id = transcript_result["video_id"]
    duration = transcript_result["duration_seconds"]

    # Step 2: Run compliance analysis on transcript
    if detail_level == "quick":
        report = quick_scan_impl(transcript)
    elif detail_level == "deep":
        report = deep_review_impl(transcript)
    else:
        report = full_analysis_impl(transcript)

    # Enrich with video metadata
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
# ALL_TOOLS registry
# ---------------------------------------------------------------------------

ALL_TOOLS = {
    "quick": {
        "tool": quick_scan,
        "credits": 1,
        "skill": AgentSkill(
            id="quick_scan",
            name="Quick Compliance Scan",
            description="Quick scan for legal compliance issues in content. Costs 1 credit.",
            tags=["compliance", "legal", "scan", "quick"],
        ),
    },
    "full": {
        "tool": full_analysis,
        "credits": 5,
        "skill": AgentSkill(
            id="full_analysis",
            name="Full Compliance Analysis",
            description="Detailed compliance analysis with per-section risk scores. Costs 5 credits.",
            tags=["compliance", "legal", "analysis", "detailed"],
        ),
    },
    "deep": {
        "tool": deep_review,
        "credits": 10,
        "skill": AgentSkill(
            id="deep_review",
            name="Deep Compliance Review",
            description="Comprehensive legal review with citations and rewrite suggestions. Costs 10 credits.",
            tags=["compliance", "legal", "review", "citations"],
        ),
    },
    "video": {
        "tool": scan_video,
        "credits": 8,
        "skill": AgentSkill(
            id="scan_video",
            name="YouTube Video Compliance Scan",
            description="Extract transcript from a YouTube video and run compliance analysis. Costs 8 credits.",
            tags=["compliance", "legal", "youtube", "video", "transcript"],
        ),
    },
}


def resolve_tools(tool_names: list[str] | None = None):
    """Resolve tool short names to (tools, credit_map, skills)."""
    names = tool_names if tool_names else list(ALL_TOOLS.keys())
    tools = []
    credit_map = {}
    skills = []
    for name in names:
        entry = ALL_TOOLS[name]
        fn = entry["tool"]
        tools.append(fn)
        credit_map[fn.__name__] = entry["credits"]
        skills.append(entry["skill"])
    return tools, credit_map, skills


# Module-level defaults
CREDIT_MAP = {fn.__name__: e["credits"] for fn, e in
               ((ALL_TOOLS[n]["tool"], ALL_TOOLS[n]) for n in ALL_TOOLS)}
TOOLS = [ALL_TOOLS[n]["tool"] for n in ALL_TOOLS]

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


def _build_system_prompt(tools_list):
    """Build a system prompt that only mentions the available tools."""
    tool_names = {t.__name__ for t in tools_list}
    lines = ["You are a compliance checker agent for content creators.\n"]
    if "quick_scan" in tool_names:
        lines.append("- **quick_scan** (1 credit) - Quick compliance scan for obvious issues.")
    if "full_analysis" in tool_names:
        lines.append("- **full_analysis** (5 credits) - Detailed compliance analysis with risk scores.")
    if "deep_review" in tool_names:
        lines.append("- **deep_review** (10 credits) - Comprehensive review with legal citations.")
    if "scan_video" in tool_names:
        lines.append("- **scan_video** (8 credits) - Extract YouTube transcript and run compliance analysis.")
    lines.append(
        "\nChoose the appropriate tool based on the user's request. "
        "Always explain findings clearly and recommend actions."
    )
    return "\n".join(lines)


def create_plain_agent(model, tool_names: list[str] | None = None) -> Agent:
    """Create a Strands agent with plain (non-payment) compliance tools."""
    if tool_names:
        tools, _, _ = resolve_tools(tool_names)
        prompt = _build_system_prompt(tools)
    else:
        tools = TOOLS
        prompt = SYSTEM_PROMPT
    return Agent(
        model=model,
        tools=tools,
        system_prompt=prompt,
    )
