"""Compliance checking tool — analyzes content for legal/regulatory risks.

Supports OpenAI (default) and AWS Bedrock Claude via COMPLIANCE_LLM_PROVIDER env var.
"""

import json
import os
import tempfile
from datetime import datetime, timezone

from openai import OpenAI


COMPLIANCE_SYSTEM_PROMPT = """\
You are an expert legal compliance analyst specializing in content creator regulations.
You analyze text content (scripts, transcripts, social media posts) for potential legal
and regulatory compliance issues.

Analyze the provided content and produce a structured compliance report covering:

1. **FTC Compliance** — Undisclosed sponsorships, affiliate links, misleading endorsements
2. **Health/Medical Claims** — Unsubstantiated health claims, medical advice without credentials,
   FDA-regulated claims (supplements, treatments, cures)
3. **Financial Advice** — Investment advice without SEC/FINRA registration, income guarantees,
   misleading earnings claims
4. **Privacy/Defamation** — Potential defamation, unauthorized personal info disclosure,
   privacy violations
5. **Copyright/IP** — Potential copyright issues, trademark misuse
6. **Platform Policy** — Content that may violate YouTube/TikTok/Instagram community guidelines

For EACH issue found, provide:
- The exact problematic text (quote it)
- The risk level: HIGH / MEDIUM / LOW
- The specific regulation or law it may violate — USE THE EXACT LEGAL CITATION.
  Examples: "16 CFR Part 255", "FTC Act Section 5", "21 CFR Part 101.13",
  "SEC Rule 10b-5", "COPPA (15 U.S.C. §6501)", "CAN-SPAM Act (15 U.S.C. §7701)"
- A "regulation_id" field with a short machine-readable key for the regulation.
  Use one of: "16cfr255", "ftc_act_s5", "21cfr101", "21cfr343", "sec_10b5",
  "finra_2210", "coppa", "canspam", "lanham_act", "dmca", "fdca",
  "ftc_health_claims", "ftc_endorsement_guides", "sec_investment_advisers",
  "state_consumer_protection", "yt_community_guidelines", "ig_community_guidelines",
  "tiktok_community_guidelines", "hipaa", "ferpa", "ccpa", "gdpr"
  If none match exactly, use the closest one or create a descriptive key.
- A recommended fix

Return your response in this EXACT JSON format:
{
  "overall_risk": "HIGH|MEDIUM|LOW",
  "summary": "2-3 sentence summary of the main compliance concerns",
  "issues": [
    {
      "category": "FTC|Health|Financial|Privacy|Copyright|Platform",
      "risk_level": "HIGH|MEDIUM|LOW",
      "problematic_text": "exact quote from content",
      "regulation": "specific law or regulation with full citation",
      "regulation_id": "machine_readable_key",
      "explanation": "why this is a compliance risk",
      "recommended_fix": "how to fix it"
    }
  ],
  "compliance_score": 0-100,
  "safe_sections": "brief note on what parts of the content are compliant",
  "disclaimer": "This is AI-generated analysis, not legal advice. Consult a licensed attorney."
}

For compliance_score: 100 = fully compliant, 0 = severe violations everywhere.
Calculate based on number and severity of issues found.

Be thorough but avoid false positives. Only flag genuine compliance risks."""


# ---------------------------------------------------------------------------
# Regulation link resolver — maps regulation IDs to official source URLs
# ---------------------------------------------------------------------------
REGULATION_LINKS: dict[str, dict[str, str]] = {
    # FTC
    "16cfr255": {
        "name": "FTC Endorsement Guides (16 CFR Part 255)",
        "url": "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255",
    },
    "ftc_act_s5": {
        "name": "FTC Act Section 5 — Unfair or Deceptive Acts",
        "url": "https://www.law.cornell.edu/uscode/text/15/45",
    },
    "ftc_endorsement_guides": {
        "name": "FTC Endorsement Guides (16 CFR Part 255)",
        "url": "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255",
    },
    "ftc_health_claims": {
        "name": "FTC Health Claims Policy",
        "url": "https://www.ftc.gov/news-events/topics/truth-advertising/health-claims",
    },
    # FDA / Health
    "21cfr101": {
        "name": "FDA Food Labeling (21 CFR Part 101)",
        "url": "https://www.ecfr.gov/current/title-21/chapter-I/subchapter-B/part-101",
    },
    "21cfr343": {
        "name": "FDA OTC Drug Labeling (21 CFR Part 343)",
        "url": "https://www.ecfr.gov/current/title-21/chapter-I/subchapter-D/part-343",
    },
    "fdca": {
        "name": "Federal Food, Drug, and Cosmetic Act",
        "url": "https://www.law.cornell.edu/uscode/text/21/chapter-9",
    },
    # SEC / Financial
    "sec_10b5": {
        "name": "SEC Rule 10b-5 — Anti-Fraud",
        "url": "https://www.law.cornell.edu/cfr/text/17/section-240.10b-5",
    },
    "finra_2210": {
        "name": "FINRA Rule 2210 — Communications with the Public",
        "url": "https://www.finra.org/rules-guidance/rulebooks/finra-rules/2210",
    },
    "sec_investment_advisers": {
        "name": "Investment Advisers Act of 1940",
        "url": "https://www.law.cornell.edu/uscode/text/15/chapter-2D/subchapter-II",
    },
    # Privacy
    "coppa": {
        "name": "COPPA — Children's Online Privacy Protection Act",
        "url": "https://www.law.cornell.edu/uscode/text/15/chapter-91",
    },
    "canspam": {
        "name": "CAN-SPAM Act",
        "url": "https://www.law.cornell.edu/uscode/text/15/chapter-103",
    },
    "hipaa": {
        "name": "HIPAA Privacy Rule",
        "url": "https://www.hhs.gov/hipaa/for-professionals/privacy/index.html",
    },
    "ccpa": {
        "name": "California Consumer Privacy Act (CCPA)",
        "url": "https://oag.ca.gov/privacy/ccpa",
    },
    "gdpr": {
        "name": "EU General Data Protection Regulation",
        "url": "https://gdpr-info.eu/",
    },
    "ferpa": {
        "name": "FERPA — Family Educational Rights and Privacy Act",
        "url": "https://www.law.cornell.edu/uscode/text/20/1232g",
    },
    # IP / Copyright
    "lanham_act": {
        "name": "Lanham Act — Trademark Law",
        "url": "https://www.law.cornell.edu/uscode/text/15/chapter-22",
    },
    "dmca": {
        "name": "DMCA — Digital Millennium Copyright Act",
        "url": "https://www.law.cornell.edu/uscode/text/17/chapter-12",
    },
    # Platform policies
    "yt_community_guidelines": {
        "name": "YouTube Community Guidelines",
        "url": "https://www.youtube.com/howyoutubeworks/policies/community-guidelines/",
    },
    "ig_community_guidelines": {
        "name": "Instagram Community Guidelines",
        "url": "https://help.instagram.com/477434105621119",
    },
    "tiktok_community_guidelines": {
        "name": "TikTok Community Guidelines",
        "url": "https://www.tiktok.com/community-guidelines",
    },
    # State laws
    "state_consumer_protection": {
        "name": "State Consumer Protection Laws",
        "url": "https://www.usa.gov/state-consumer",
    },
}


def _enrich_regulation_links(report: dict) -> dict:
    """Add official regulation URLs to each issue based on regulation_id."""
    issues = report.get("issues", [])
    for issue in issues:
        reg_id = issue.get("regulation_id", "")
        if reg_id and reg_id in REGULATION_LINKS:
            link_info = REGULATION_LINKS[reg_id]
            issue["regulation_url"] = link_info["url"]
            issue["regulation_name"] = link_info["name"]
    return report


def quick_scan_impl(content: str) -> dict:
    """Quick compliance scan — flags obvious issues in short content.

    Args:
        content: Text content to scan (script, transcript, post).

    Returns:
        dict with status, content (for Strands), and compliance report.
    """
    return _analyze_compliance(
        content,
        max_tokens=2000,
        detail_level="quick",
    )


def full_analysis_impl(content: str, focus: str = "all") -> dict:
    """Full compliance analysis — detailed per-section report.

    Args:
        content: Text content to analyze.
        focus: Focus area - 'all', 'health', 'financial', 'ftc', 'privacy'.

    Returns:
        dict with status, content (for Strands), and detailed compliance report.
    """
    focus_instruction = ""
    if focus != "all":
        focus_map = {
            "health": "Focus especially on health and medical claims compliance.",
            "financial": "Focus especially on financial advice and SEC/FINRA compliance.",
            "ftc": "Focus especially on FTC disclosure and endorsement compliance.",
            "privacy": "Focus especially on privacy, defamation, and personal data.",
        }
        focus_instruction = focus_map.get(focus, "")

    return _analyze_compliance(
        content,
        max_tokens=4000,
        detail_level="full",
        extra_instruction=focus_instruction,
    )


def deep_review_impl(content: str) -> dict:
    """Deep compliance review — full analysis + legal citations + edit suggestions.

    Args:
        content: Text content to deeply review.

    Returns:
        dict with status, content (for Strands), and comprehensive compliance report.
    """
    return _analyze_compliance(
        content,
        max_tokens=4096,
        detail_level="deep",
        extra_instruction=(
            "Additionally, for each issue:\n"
            "- Cite the specific section of the relevant law (e.g., FTC Act Section 5, "
            "21 CFR Part 101, SEC Rule 10b-5)\n"
            "- Provide a rewritten version of the problematic text that would be compliant\n"
            "- Estimate the potential penalty range if enforced\n"
            "Add a 'legal_citations' array to the JSON with full citations."
        ),
    )


def generate_report_impl(content: str, detail_level: str = "full") -> dict:
    """Generate a compliance report and save an HTML file to a temp path.

    Runs the compliance analysis, returns both the text report and a path
    to a saved HTML file that can be opened in a browser or printed to PDF.

    Args:
        content: Text content to analyze (script, transcript, post).
        detail_level: One of 'quick', 'full', or 'deep'.

    Returns:
        dict with status, content (for Strands), report, html_report string,
        and html_report_path pointing to the saved HTML file.
    """
    detail_map = {
        "quick": quick_scan_impl,
        "full": full_analysis_impl,
        "deep": deep_review_impl,
    }
    analyze_fn = detail_map.get(detail_level, full_analysis_impl)
    result = analyze_fn(content)

    if result.get("status") != "success":
        return result

    html_report = result.get("html_report", "")

    # Write HTML to a temporary file
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".html",
        prefix="compliance_report_",
        delete=False,
    )
    try:
        tmp.write(html_report)
        tmp.flush()
        html_path = tmp.name
    finally:
        tmp.close()

    result["html_report_path"] = html_path
    text_report = result["content"][0]["text"] if result.get("content") else ""
    result["content"] = [
        {"text": f"{text_report}\n\nHTML report saved to: {html_path}"}
    ]

    return result


def _analyze_compliance(
    content: str,
    max_tokens: int = 1000,
    detail_level: str = "quick",
    extra_instruction: str = "",
) -> dict:
    """Core compliance analysis using LLM.

    Supports OpenAI (default) or Bedrock Claude via COMPLIANCE_LLM_PROVIDER env var.
    """
    provider = os.getenv("COMPLIANCE_LLM_PROVIDER", "openai")

    system_prompt = COMPLIANCE_SYSTEM_PROMPT
    if extra_instruction:
        system_prompt += f"\n\n{extra_instruction}"

    user_message = (
        f"Analyze the following content for compliance issues.\n"
        f"Detail level: {detail_level}\n\n"
        f"--- CONTENT START ---\n{content[:8000]}\n--- CONTENT END ---"
    )

    try:
        if provider == "bedrock":
            response_text = _call_bedrock(system_prompt, user_message, max_tokens)
        elif provider == "anthropic":
            response_text = _call_anthropic(system_prompt, user_message, max_tokens)
        else:
            response_text = _call_openai(system_prompt, user_message, max_tokens)

        # Try to parse as JSON
        report = _parse_report(response_text)

        # Enrich with official regulation URLs
        report = _enrich_regulation_links(report)

        # Build human-readable summary
        readable = _format_readable(report, detail_level)

        # Build HTML report
        html_report = _format_html_report(report, detail_level)

        return {
            "status": "success",
            "content": [{"text": readable}],
            "report": report,
            "html_report": html_report,
            "detail_level": detail_level,
        }

    except Exception as e:
        return {
            "status": "error",
            "content": [{"text": f"Compliance analysis failed: {e}"}],
            "report": {},
            "detail_level": detail_level,
        }


def _call_openai(system_prompt: str, user_message: str, max_tokens: int) -> str:
    """Call OpenAI-compatible API."""
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
    model_id = os.environ.get("COMPLIANCE_MODEL_ID", os.environ.get("MODEL_ID", "gpt-4o-mini"))

    completion = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    return completion.choices[0].message.content or "{}"


def _call_anthropic(system_prompt: str, user_message: str, max_tokens: int) -> str:
    """Call Anthropic API directly."""
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    model_id = os.environ.get(
        "COMPLIANCE_MODEL_ID", "claude-haiku-4-5-20251001"
    )

    response = client.messages.create(
        model=model_id,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def _call_bedrock(system_prompt: str, user_message: str, max_tokens: int) -> str:
    """Call AWS Bedrock Claude."""
    import boto3

    region = os.environ.get("AWS_REGION", "us-west-2")
    model_id = os.environ.get(
        "BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    )

    client = boto3.client("bedrock-runtime", region_name=region)
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}],
        }),
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


def _parse_report(text: str) -> dict:
    """Parse JSON from LLM response, handling markdown code blocks and extra text."""
    import re

    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Find the outermost JSON object { ... }
    start = text.find("{")
    if start != -1:
        depth = 0
        end = start
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    return {"raw_response": text, "parse_error": True}


def _format_readable(report: dict, detail_level: str) -> str:
    """Format the compliance report as human-readable text."""
    if report.get("parse_error"):
        return report.get("raw_response", "Analysis complete but could not parse report.")

    lines = []
    risk = report.get("overall_risk", "UNKNOWN")
    risk_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(risk, "⚪")

    lines.append(f"{'='*60}")
    lines.append(f"  COMPLIANCE REPORT — {risk_emoji} Overall Risk: {risk}")
    lines.append(f"{'='*60}")
    lines.append(f"\n📋 Summary: {report.get('summary', 'N/A')}\n")

    issues = report.get("issues", [])
    if issues:
        lines.append(f"⚠️  {len(issues)} Issue(s) Found:\n")
        for i, issue in enumerate(issues, 1):
            risk_e = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(
                issue.get("risk_level", ""), "⚪"
            )
            lines.append(f"  {i}. {risk_e} [{issue.get('category', '?')}] {issue.get('risk_level', '?')}")
            lines.append(f"     Quote: \"{issue.get('problematic_text', 'N/A')}\"")
            lines.append(f"     Regulation: {issue.get('regulation', 'N/A')}")
            reg_url = issue.get("regulation_url", "")
            if reg_url:
                lines.append(f"     Source: {reg_url}")
            lines.append(f"     Explanation: {issue.get('explanation', 'N/A')}")
            lines.append(f"     Fix: {issue.get('recommended_fix', 'N/A')}")

            if detail_level == "deep":
                citation = issue.get("legal_citation", "")
                rewrite = issue.get("compliant_rewrite", "")
                penalty = issue.get("penalty_range", "")
                if citation:
                    lines.append(f"     📖 Citation: {citation}")
                if rewrite:
                    lines.append(f"     ✏️  Rewrite: {rewrite}")
                if penalty:
                    lines.append(f"     💰 Penalty: {penalty}")
            lines.append("")
    else:
        lines.append("✅ No compliance issues found.\n")

    safe = report.get("safe_sections", "")
    if safe:
        lines.append(f"✅ Safe: {safe}\n")

    lines.append(f"⚖️  {report.get('disclaimer', 'This is AI analysis, not legal advice.')}")
    lines.append(f"{'='*60}")

    return "\n".join(lines)


def _format_html_report(report: dict, detail_level: str) -> str:
    """Format the compliance report as a self-contained HTML document.

    Generates a professional, print-friendly HTML report with inline CSS,
    color-coded risk levels, styled issue cards, and a legal-document aesthetic.
    """
    if report.get("parse_error"):
        raw = report.get("raw_response", "Analysis complete but could not parse report.")
        return f"<html><body><pre>{raw}</pre></body></html>"

    risk = report.get("overall_risk", "UNKNOWN")
    summary = report.get("summary", "N/A")
    issues = report.get("issues", [])
    safe_sections = report.get("safe_sections", "")
    disclaimer = report.get("disclaimer", "This is AI-generated analysis, not legal advice. Consult a licensed attorney.")
    generated_at = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")

    risk_colors = {
        "HIGH": {"bg": "#dc2626", "text": "#ffffff", "light": "#fef2f2", "border": "#fca5a5"},
        "MEDIUM": {"bg": "#d97706", "text": "#ffffff", "light": "#fffbeb", "border": "#fcd34d"},
        "LOW": {"bg": "#16a34a", "text": "#ffffff", "light": "#f0fdf4", "border": "#86efac"},
    }
    risk_style = risk_colors.get(risk, {"bg": "#6b7280", "text": "#ffffff", "light": "#f9fafb", "border": "#d1d5db"})

    category_icons = {
        "FTC": "shield",
        "Health": "heart-pulse",
        "Financial": "dollar-sign",
        "Privacy": "eye-off",
        "Copyright": "file-text",
        "Platform": "monitor",
    }

    # Count issues by risk level
    high_count = sum(1 for i in issues if i.get("risk_level") == "HIGH")
    medium_count = sum(1 for i in issues if i.get("risk_level") == "MEDIUM")
    low_count = sum(1 for i in issues if i.get("risk_level") == "LOW")

    # Build issue cards HTML
    issue_cards_html = ""
    for idx, issue in enumerate(issues, 1):
        i_risk = issue.get("risk_level", "UNKNOWN")
        i_style = risk_colors.get(i_risk, risk_colors.get("LOW"))
        category = issue.get("category", "General")
        icon_name = category_icons.get(category, "alert-circle")

        # SVG icons for each category
        icon_svgs = {
            "shield": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
            "heart-pulse": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19.5 12.572l-7.5 7.428-7.5-7.428A5 5 0 1 1 12 6.006a5 5 0 1 1 7.5 6.572"/><path d="M12 6v4l2 2"/></svg>',
            "dollar-sign": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
            "eye-off": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>',
            "file-text": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
            "monitor": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
            "alert-circle": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
        }
        icon_svg = icon_svgs.get(icon_name, icon_svgs["alert-circle"])

        # Deep-review extras
        deep_extras = ""
        if detail_level == "deep":
            citation = issue.get("legal_citation", "")
            rewrite = issue.get("compliant_rewrite", "")
            penalty = issue.get("penalty_range", "")
            if citation:
                deep_extras += f"""
                <div style="margin-top: 12px; padding: 10px 14px; background: #f5f3ff; border-left: 3px solid #7c3aed; border-radius: 4px;">
                    <strong style="color: #7c3aed; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em;">Legal Citation</strong>
                    <p style="margin: 4px 0 0; color: #4c1d95; font-size: 0.9rem;">{citation}</p>
                </div>"""
            if rewrite:
                deep_extras += f"""
                <div style="margin-top: 8px; padding: 10px 14px; background: #ecfdf5; border-left: 3px solid #059669; border-radius: 4px;">
                    <strong style="color: #059669; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em;">Compliant Rewrite</strong>
                    <p style="margin: 4px 0 0; color: #065f46; font-size: 0.9rem; font-style: italic;">{rewrite}</p>
                </div>"""
            if penalty:
                deep_extras += f"""
                <div style="margin-top: 8px; padding: 10px 14px; background: #fef2f2; border-left: 3px solid #dc2626; border-radius: 4px;">
                    <strong style="color: #dc2626; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em;">Potential Penalty</strong>
                    <p style="margin: 4px 0 0; color: #991b1b; font-size: 0.9rem;">{penalty}</p>
                </div>"""

        issue_cards_html += f"""
        <div style="background: #ffffff; border: 1px solid #e5e7eb; border-left: 5px solid {i_style['bg']}; border-radius: 8px; padding: 24px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); page-break-inside: avoid;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                <div style="width: 40px; height: 40px; background: {i_style['light']}; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: {i_style['bg']}; flex-shrink: 0;">
                    {icon_svg}
                </div>
                <div style="flex: 1;">
                    <span style="font-weight: 700; font-size: 1rem; color: #1f2937;">Issue #{idx}: {category}</span>
                </div>
                <span style="background: {i_style['bg']}; color: {i_style['text']}; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">{i_risk} RISK</span>
            </div>

            <div style="background: #f9fafb; border-radius: 6px; padding: 14px 18px; margin-bottom: 14px; border: 1px solid #f3f4f6;">
                <p style="margin: 0; font-style: italic; color: #374151; line-height: 1.6; font-size: 0.95rem;">"{issue.get('problematic_text', 'N/A')}"</p>
            </div>

            <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
                <tr>
                    <td style="padding: 8px 0; color: #6b7280; font-weight: 600; width: 120px; vertical-align: top;">Regulation</td>
                    <td style="padding: 8px 0; color: #1f2937;">{issue.get('regulation', 'N/A')}{f' — <a href="{issue["regulation_url"]}" target="_blank" style="color: #6366f1; text-decoration: underline;">View Official Source</a>' if issue.get("regulation_url") else ''}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #6b7280; font-weight: 600; vertical-align: top;">Explanation</td>
                    <td style="padding: 8px 0; color: #1f2937; line-height: 1.5;">{issue.get('explanation', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #6b7280; font-weight: 600; vertical-align: top;">Recommended Fix</td>
                    <td style="padding: 8px 0; color: #1f2937; line-height: 1.5;">{issue.get('recommended_fix', 'N/A')}</td>
                </tr>
            </table>
            {deep_extras}
        </div>"""

    # Safe sections callout
    safe_html = ""
    if safe_sections:
        safe_html = f"""
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px 24px; margin-bottom: 32px; page-break-inside: avoid;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                <span style="font-weight: 700; color: #15803d; font-size: 1rem;">Compliant Sections</span>
            </div>
            <p style="margin: 0; color: #166534; line-height: 1.6; font-size: 0.95rem;">{safe_sections}</p>
        </div>"""

    # No issues message
    no_issues_html = ""
    if not issues:
        no_issues_html = """
        <div style="background: #f0fdf4; border: 2px solid #86efac; border-radius: 12px; padding: 40px; text-align: center; margin-bottom: 32px;">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 16px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <h3 style="margin: 0 0 8px; color: #15803d; font-size: 1.25rem;">No Compliance Issues Found</h3>
            <p style="margin: 0; color: #166534; font-size: 0.95rem;">The analyzed content appears to be compliant with applicable regulations.</p>
        </div>"""

    # Detail level label
    detail_labels = {"quick": "Quick Scan", "full": "Full Analysis", "deep": "Deep Review"}
    detail_label = detail_labels.get(detail_level, detail_level.title())

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compliance Report - {generated_at}</title>
    <style>
        @media print {{
            body {{ margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .header {{ break-after: avoid; }}
            .issue-card {{ break-inside: avoid; }}
            .no-print {{ display: none !important; }}
        }}
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: #f8fafc;
            color: #1f2937;
            line-height: 1.6;
        }}
        .container {{
            max-width: 860px;
            margin: 0 auto;
            padding: 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; padding: 40px 48px; border-radius: 0 0 12px 12px;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                        <h1 style="margin: 0; font-size: 1.5rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase;">Compliance Report</h1>
                    </div>
                    <p style="margin: 0; color: #94a3b8; font-size: 0.85rem;">{detail_label} &middot; Generated {generated_at}</p>
                </div>
                <div style="text-align: right;">
                    <span style="background: {risk_style['bg']}; color: {risk_style['text']}; padding: 8px 20px; border-radius: 24px; font-size: 0.85rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; display: inline-block; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">{risk} RISK</span>
                </div>
            </div>
        </div>

        <!-- Body -->
        <div style="padding: 32px 48px 48px;">

            <!-- Summary -->
            <div style="background: {risk_style['light']}; border: 1px solid {risk_style['border']}; border-radius: 8px; padding: 20px 24px; margin-bottom: 32px;">
                <h2 style="margin: 0 0 8px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #6b7280;">Executive Summary</h2>
                <p style="margin: 0; font-size: 1rem; line-height: 1.7; color: #1f2937;">{summary}</p>
            </div>

            <!-- Stats Row -->
            <div style="display: flex; gap: 16px; margin-bottom: 32px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 120px; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px 20px; text-align: center;">
                    <div style="font-size: 2rem; font-weight: 800; color: #1f2937;">{len(issues)}</div>
                    <div style="font-size: 0.8rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Total Issues</div>
                </div>
                <div style="flex: 1; min-width: 120px; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px 20px; text-align: center;">
                    <div style="font-size: 2rem; font-weight: 800; color: #dc2626;">{high_count}</div>
                    <div style="font-size: 0.8rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">High Risk</div>
                </div>
                <div style="flex: 1; min-width: 120px; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px 20px; text-align: center;">
                    <div style="font-size: 2rem; font-weight: 800; color: #d97706;">{medium_count}</div>
                    <div style="font-size: 0.8rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Medium Risk</div>
                </div>
                <div style="flex: 1; min-width: 120px; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px 20px; text-align: center;">
                    <div style="font-size: 2rem; font-weight: 800; color: #16a34a;">{low_count}</div>
                    <div style="font-size: 0.8rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Low Risk</div>
                </div>
            </div>

            <!-- Issues -->
            {f'<h2 style="font-size: 1.1rem; font-weight: 700; color: #1f2937; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 2px solid #e5e7eb;">Issues Identified</h2>' if issues else ''}
            {no_issues_html}
            {issue_cards_html}

            <!-- Safe Sections -->
            {safe_html}

            <!-- Disclaimer -->
            <div style="margin-top: 40px; padding-top: 24px; border-top: 1px solid #e5e7eb;">
                <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 16px 20px; display: flex; align-items: flex-start; gap: 12px;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0; margin-top: 2px;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                    <div>
                        <p style="margin: 0 0 4px; font-weight: 700; color: #92400e; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Legal Disclaimer</p>
                        <p style="margin: 0; color: #92400e; font-size: 0.85rem; line-height: 1.5;">{disclaimer}</p>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div style="margin-top: 24px; text-align: center; color: #9ca3af; font-size: 0.75rem;">
                <p style="margin: 0;">Compliance Report generated by AI Compliance Analyzer</p>
                <p style="margin: 4px 0 0;">{generated_at}</p>
            </div>

        </div>
    </div>
</body>
</html>"""

    return html
