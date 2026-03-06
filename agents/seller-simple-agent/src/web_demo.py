"""
Web demo server — beautiful product landing page + free REST API.

Serves the landing page and provides direct compliance scanning
without payment (this is the demo/product frontend). Payment flow
happens when other AGENTS call via A2A or MCP.

Usage:
    poetry run web-demo
    DEMO_PORT=9090 poetry run web-demo
"""

import json
import os
import threading
import time
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import List

from dotenv import load_dotenv

load_dotenv()

import uvicorn
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Security constants
# ---------------------------------------------------------------------------
_MAX_CONTENT_LENGTH = 50_000   # max characters for text scans
_MAX_URL_LENGTH = 2048         # max characters for URLs
_RATE_LIMIT_MAX = 30           # max requests per window per IP
_RATE_LIMIT_WINDOW = 60        # window in seconds

# ---------------------------------------------------------------------------
# In-memory rate limiter (per-IP, resets each minute window)
# ---------------------------------------------------------------------------
_rate_limit_store: dict[str, tuple[int, float]] = {}

def _check_rate_limit(client_ip: str) -> bool:
    """Return True if request is allowed, False if rate-limited."""
    now = time.time()
    entry = _rate_limit_store.get(client_ip)
    if entry is None or (now - entry[1]) >= _RATE_LIMIT_WINDOW:
        _rate_limit_store[client_ip] = (1, now)
        return True
    count, window_start = entry
    if count >= _RATE_LIMIT_MAX:
        return False
    _rate_limit_store[client_ip] = (count + 1, window_start)
    return True


def _get_client_ip(request: Request) -> str:
    """Extract client IP from request, respecting X-Forwarded-For."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _error_response(status_code: int, message: str) -> JSONResponse:
    """Return a consistent JSON error response."""
    return JSONResponse(
        status_code=status_code,
        content={"error": message, "status": status_code},
    )

from .tools.compliance_check import (
    deep_review_impl,
    full_analysis_impl,
    quick_scan_impl,
)
from .tools.youtube_transcript import get_transcript_impl

DEMO_PORT = int(os.getenv("DEMO_PORT", "8080"))

# Resolve landing page path relative to project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_LANDING_DIR = _PROJECT_ROOT / "landing"

# ---------------------------------------------------------------------------
# In-memory state for stats & history (resets on restart — fine for hackathon)
# ---------------------------------------------------------------------------
_start_time: float = time.time()
_scan_counter: int = 0          # auto-incrementing scan ID
_total_scans: int = 0
_text_scans: int = 0
_video_scans: int = 0
_issues_found: int = 0
_risk_scores: list = []         # list of numeric risk scores for averaging
_scan_history: list = []        # last N scan results (capped at 50)
_webhooks: list[str] = []       # registered webhook URLs

_HISTORY_MAX = 50

_RISK_SCORE_MAP = {"HIGH": 9, "MEDIUM": 5, "LOW": 2}


def _next_scan_id() -> str:
    """Generate a unique scan ID."""
    global _scan_counter
    _scan_counter += 1
    return f"scan_{_scan_counter}"


def _extract_risk_level(report: dict) -> str:
    """Extract overall risk level from the compliance report dict."""
    return report.get("overall_risk", "UNKNOWN")


def _extract_issues_count(report: dict) -> int:
    """Count issues from the compliance report dict."""
    issues = report.get("issues", [])
    return len(issues) if isinstance(issues, list) else 0


def _record_scan(
    scan_type: str,
    content_preview: str,
    detail_level: str,
    report: dict,
    status: str = "completed",
    html_report: str = "",
) -> None:
    """Record a scan into stats counters and history list."""
    global _total_scans, _text_scans, _video_scans, _issues_found

    _total_scans += 1
    if scan_type == "text":
        _text_scans += 1
    elif scan_type == "video":
        _video_scans += 1

    risk_level = _extract_risk_level(report)
    issues_count = _extract_issues_count(report)
    _issues_found += issues_count

    numeric_score = _RISK_SCORE_MAP.get(risk_level, 0)
    if numeric_score:
        _risk_scores.append(numeric_score)

    entry = {
        "id": _next_scan_id(),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "type": scan_type,
        "content_preview": content_preview[:100],
        "detail_level": detail_level,
        "risk_level": risk_level,
        "issues_count": issues_count,
        "status": status,
        "html_report": html_report,
    }
    _scan_history.append(entry)

    # Cap history at _HISTORY_MAX
    if len(_scan_history) > _HISTORY_MAX:
        _scan_history.pop(0)

    # Fire webhooks asynchronously (exclude bulky html_report)
    if _webhooks:
        payload = json.dumps({k: v for k, v in entry.items() if k != "html_report"}).encode()
        for url in list(_webhooks):
            threading.Thread(
                target=_fire_webhook, args=(url, payload), daemon=True
            ).start()


def _fire_webhook(url: str, payload: bytes) -> None:
    """POST scan result to a webhook URL (best-effort, no retries)."""
    try:
        req = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass  # best-effort — don't crash on webhook failure


app = FastAPI(
    title="Compliance Checker — Demo",
    description=(
        "Free product demo for the AI-powered compliance checker. "
        "Scan content and YouTube videos for FTC, health, financial, "
        "and privacy compliance issues."
    ),
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — restrict to known local origins
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:8080",
        "http://localhost:9000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class ScanRequest(BaseModel):
    content: str
    detail_level: str = "quick"  # quick | full | deep


class VideoScanRequest(BaseModel):
    youtube_url: str
    detail_level: str = "quick"  # quick | full | deep


class BatchScanItem(BaseModel):
    content: str
    detail_level: str = "quick"  # quick | full | deep


class ScanUrlRequest(BaseModel):
    url: str
    detail_level: str = "quick"  # quick | full | deep


class WebhookRegisterRequest(BaseModel):
    url: str


class BatchScanRequest(BaseModel):
    items: List[BatchScanItem] = Field(..., min_length=1, max_length=20)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health() -> JSONResponse:
    """Health check."""
    return JSONResponse(content={
        "status": "ok",
        "service": "compliance-checker-demo",
        "version": "1.0.0",
    })


@app.get("/api/demo")
async def demo() -> JSONResponse:
    """Return a pre-built demo scan result for instant showcase.

    Judges and visitors can hit this endpoint to see what a compliance
    report looks like without waiting for AI inference.
    """
    return JSONResponse(content={
        "status": "success",
        "detail_level": "full",
        "demo": True,
        "report": {
            "overall_risk": "HIGH",
            "summary": "Content contains multiple serious compliance violations including unsubstantiated health claims, undisclosed sponsorship, and misleading financial advice.",
            "issues": [
                {
                    "category": "Health",
                    "risk_level": "HIGH",
                    "problematic_text": "I lost 30 pounds in just 2 weeks! It literally cures inflammation and reverses aging.",
                    "regulation": "FTC Health Claims Standards; FDA Act (21 U.S.C. \u00a7321)",
                    "regulation_id": "ftc_health_claims",
                    "explanation": "Unsubstantiated weight loss and disease cure claims. The FTC requires that health claims be backed by competent and reliable scientific evidence.",
                    "recommended_fix": "Replace with: 'I've been using KetoBlast Pro as part of my fitness routine. Individual results may vary. This is not medical advice.'",
                    "regulation_url": "https://www.ftc.gov/news-events/topics/truth-advertising/health-claims",
                    "regulation_name": "FTC Health Claims Policy",
                },
                {
                    "category": "FTC",
                    "risk_level": "HIGH",
                    "problematic_text": "Use my code HEALTH50 for 50% off at the link in my bio.",
                    "regulation": "16 CFR Part 255 - FTC Endorsement Guides",
                    "regulation_id": "16cfr255",
                    "explanation": "Affiliate/sponsored content without clear disclosure. The FTC requires clear and conspicuous disclosure of material connections.",
                    "recommended_fix": "Add '#ad' or '#sponsored' prominently at the beginning. Verbally state: 'This is a paid partnership with KetoBlast Pro.'",
                    "regulation_url": "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255",
                    "regulation_name": "FTC Endorsement Guides (16 CFR Part 255)",
                },
                {
                    "category": "Financial",
                    "risk_level": "HIGH",
                    "problematic_text": "This new crypto token is guaranteed to 10x by next month - not financial advice lol but seriously put your savings in it.",
                    "regulation": "SEC Rule 10b-5 - Anti-Fraud; FINRA Rule 2210",
                    "regulation_id": "sec_10b5",
                    "explanation": "Guaranteed investment returns constitute securities fraud. 'Not financial advice' disclaimers do not provide legal protection when specific investment recommendations are made.",
                    "recommended_fix": "Remove entirely. If discussing crypto, state: 'I personally hold [token]. This is not investment advice. All investments carry risk of loss. Do your own research.'",
                    "regulation_url": "https://www.law.cornell.edu/cfr/text/17/section-240.10b-5",
                    "regulation_name": "SEC Rule 10b-5 \u2014 Anti-Fraud",
                },
                {
                    "category": "Health",
                    "risk_level": "MEDIUM",
                    "problematic_text": "My doctor was SHOCKED.",
                    "regulation": "FTC Act Section 5 - Deceptive Practices",
                    "regulation_id": "ftc_act_s5",
                    "explanation": "Implies medical professional endorsement of the product's efficacy without substantiation. Creates misleading impression of professional validation.",
                    "recommended_fix": "Remove claim or provide actual documented medical opinion with proper context and disclaimers.",
                    "regulation_url": "https://www.law.cornell.edu/uscode/text/15/45",
                    "regulation_name": "FTC Act Section 5 \u2014 Unfair or Deceptive Acts",
                },
            ],
            "compliance_score": 15,
            "safe_sections": "No compliant sections identified in this content sample.",
            "disclaimer": "This is AI-generated analysis, not legal advice. Consult a licensed attorney.",
        },
        "compliance_score": 15,
        "elapsed_seconds": 0.001,
        "note": "This is a pre-built demo result. Use POST /api/scan for live analysis.",
    })


@app.post("/api/scan")
async def scan(request: Request, body: ScanRequest) -> JSONResponse:
    """Scan text content for compliance issues (no payment required).

    Accepts JSON with ``content`` (the text to scan) and an optional
    ``detail_level`` of ``quick``, ``full``, or ``deep``.
    """
    # Rate limiting
    if not _check_rate_limit(_get_client_ip(request)):
        return _error_response(429, "Rate limit exceeded. Max 30 requests per minute.")

    # Input validation
    content = body.content.strip()
    if not content:
        return _error_response(400, "Content must not be empty.")
    if len(content) > _MAX_CONTENT_LENGTH:
        return _error_response(400, f"Content too long. Maximum {_MAX_CONTENT_LENGTH} characters.")

    start = time.time()

    try:
        dispatch = {
            "quick": lambda: quick_scan_impl(content),
            "full": lambda: full_analysis_impl(content),
            "deep": lambda: deep_review_impl(content),
        }
        handler = dispatch.get(body.detail_level, dispatch["quick"])
        result = handler()

        elapsed = round(time.time() - start, 2)

        # Track stats & history
        report = result.get("report", {})
        readable = result.get("content", [{}])[0].get("text", "")
        html_report = result.get("html_report", "")
        _record_scan(
            scan_type="text",
            content_preview=content,
            detail_level=body.detail_level,
            report=report,
            status="completed" if result.get("status") == "success" else "error",
            html_report=html_report,
        )

        return JSONResponse(content={
            "status": result.get("status", "success"),
            "detail_level": body.detail_level,
            "report": report,
            "readable": readable,
            "compliance_score": report.get("compliance_score", None),
            "elapsed_seconds": elapsed,
        })

    except Exception as exc:
        _record_scan(
            scan_type="text",
            content_preview=content,
            detail_level=body.detail_level,
            report={},
            status="error",
            html_report="",
        )
        return _error_response(500, f"Internal server error: {exc}")


@app.post("/api/scan-video")
async def scan_video(request: Request, body: VideoScanRequest) -> JSONResponse:
    """Extract a YouTube transcript and scan it for compliance issues.

    Accepts JSON with ``youtube_url`` and an optional ``detail_level``.
    Returns the compliance report together with video metadata.
    """
    # Rate limiting
    if not _check_rate_limit(_get_client_ip(request)):
        return _error_response(429, "Rate limit exceeded. Max 30 requests per minute.")

    # Input validation
    url = body.youtube_url.strip()
    if not url:
        return _error_response(400, "YouTube URL must not be empty.")
    if len(url) > _MAX_URL_LENGTH:
        return _error_response(400, f"URL too long. Maximum {_MAX_URL_LENGTH} characters.")

    start = time.time()

    # 1. Extract transcript
    try:
        transcript_result = get_transcript_impl(url)
    except Exception as exc:
        return _error_response(422, f"Failed to extract transcript: {exc}")

    if transcript_result.get("status") != "success":
        error_text = (
            transcript_result.get("content", [{}])[0].get("text", "Unknown error")
        )
        return _error_response(422, error_text)

    transcript_text = transcript_result.get("transcript", "")
    if not transcript_text:
        return _error_response(422, "Transcript was empty.")

    # 2. Run compliance scan on transcript
    try:
        dispatch = {
            "quick": lambda: quick_scan_impl(transcript_text),
            "full": lambda: full_analysis_impl(transcript_text),
            "deep": lambda: deep_review_impl(transcript_text),
        }
        handler = dispatch.get(body.detail_level, dispatch["quick"])
        result = handler()

        elapsed = round(time.time() - start, 2)

        # Track stats & history
        report = result.get("report", {})
        readable = result.get("content", [{}])[0].get("text", "")
        html_report = result.get("html_report", "")
        _record_scan(
            scan_type="video",
            content_preview=url,
            detail_level=body.detail_level,
            report=report,
            status="completed" if result.get("status") == "success" else "error",
            html_report=html_report,
        )

        return JSONResponse(content={
            "status": result.get("status", "success"),
            "detail_level": body.detail_level,
            "report": report,
            "readable": readable,
            "compliance_score": report.get("compliance_score", None),
            "video": {
                "video_id": transcript_result.get("video_id", ""),
                "duration_seconds": transcript_result.get("duration_seconds", 0),
                "segment_count": transcript_result.get("segment_count", 0),
                "transcript_length": len(transcript_text),
            },
            "elapsed_seconds": elapsed,
        })

    except Exception as exc:
        _record_scan(
            scan_type="video",
            content_preview=url,
            detail_level=body.detail_level,
            report={},
            status="error",
            html_report="",
        )
        return _error_response(500, f"Internal server error: {exc}")


@app.get("/api/stats")
async def stats() -> JSONResponse:
    """Return usage statistics since server start."""
    try:
        avg_risk = 0.0
        if _risk_scores:
            avg_risk = round(sum(_risk_scores) / len(_risk_scores), 1)

        return JSONResponse(content={
            "total_scans": _total_scans,
            "text_scans": _text_scans,
            "video_scans": _video_scans,
            "issues_found": _issues_found,
            "avg_risk_score": avg_risk,
            "uptime_seconds": round(time.time() - _start_time, 1),
        })
    except Exception as exc:
        return _error_response(500, f"Internal server error: {exc}")


@app.get("/api/history")
async def history() -> JSONResponse:
    """Return the last 50 scan results (newest first)."""
    try:
        scans = [{k: v for k, v in e.items() if k != "html_report"} for e in reversed(_scan_history)]
        return JSONResponse(content={
            "scans": scans,
            "total": len(_scan_history),
        })
    except Exception as exc:
        return _error_response(500, f"Internal server error: {exc}")


@app.post("/api/scan-batch")
async def scan_batch(request: Request, body: BatchScanRequest) -> JSONResponse:
    """Scan multiple text items for compliance issues in a single request.

    Accepts JSON with ``items`` -- an array of objects each containing
    ``content`` and an optional ``detail_level``.
    """
    # Rate limiting
    if not _check_rate_limit(_get_client_ip(request)):
        return _error_response(429, "Rate limit exceeded. Max 30 requests per minute.")

    # Validate all items up front
    for i, item in enumerate(body.items):
        content = item.content.strip()
        if not content:
            return _error_response(400, f"Item {i}: content must not be empty.")
        if len(content) > _MAX_CONTENT_LENGTH:
            return _error_response(400, f"Item {i}: content too long. Maximum {_MAX_CONTENT_LENGTH} characters.")

    results = []
    for item in body.items:
        content = item.content.strip()
        start = time.time()
        try:
            dispatch = {
                "quick": lambda c=content: quick_scan_impl(c),
                "full": lambda c=content: full_analysis_impl(c),
                "deep": lambda c=content: deep_review_impl(c),
            }
            handler = dispatch.get(item.detail_level, dispatch["quick"])
            result = handler()
            elapsed = round(time.time() - start, 2)

            report = result.get("report", {})
            readable = result.get("content", [{}])[0].get("text", "")
            html_report = result.get("html_report", "")
            _record_scan(
                scan_type="text",
                content_preview=content,
                detail_level=item.detail_level,
                report=report,
                status="completed" if result.get("status") == "success" else "error",
                html_report=html_report,
            )

            results.append({
                "status": result.get("status", "success"),
                "detail_level": item.detail_level,
                "report": report,
                "readable": readable,
                "compliance_score": report.get("compliance_score", None),
                "elapsed_seconds": elapsed,
            })
        except Exception as exc:
            _record_scan(
                scan_type="text",
                content_preview=content,
                detail_level=item.detail_level,
                report={},
                status="error",
                html_report="",
            )
            results.append({
                "status": "error",
                "detail_level": item.detail_level,
                "error": str(exc),
                "elapsed_seconds": round(time.time() - start, 2),
            })

    return JSONResponse(content={"results": results, "total": len(results)})


# ---------------------------------------------------------------------------
# Audio/Video upload → transcribe → scan
# ---------------------------------------------------------------------------

_SUPPORTED_AUDIO = {".mp3", ".mp4", ".wav", ".webm", ".m4a", ".ogg", ".flac", ".mpeg", ".mpga"}
_MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB (Groq free tier limit)


@app.post("/api/scan-upload")
async def scan_upload(
    request: Request,
    file: UploadFile = File(...),
    detail_level: str = "full",
):
    """Upload an audio/video file, transcribe it with Groq Whisper, and scan for compliance.

    Accepts audio/video files up to 25 MB. Transcribes using Groq's
    whisper-large-v3-turbo (free, ~1.4s for 5 min of audio), then runs
    compliance analysis on the transcript.
    """
    # Rate limiting
    if not _check_rate_limit(_get_client_ip(request)):
        return _error_response(429, "Rate limit exceeded. Max 30 requests per minute.")

    import tempfile
    from groq import Groq

    start = time.time()

    # Validate file
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in _SUPPORTED_AUDIO:
        return _error_response(422, f"Unsupported format: {ext}. Supported: {', '.join(sorted(_SUPPORTED_AUDIO))}")

    contents = await file.read()
    if len(contents) > _MAX_FILE_SIZE:
        return _error_response(422, f"File too large ({len(contents) // (1024*1024)}MB). Max: 25MB.")

    # Transcribe with Groq Whisper
    groq_key = os.environ.get("GROQ_API_KEY", "")
    if not groq_key:
        return _error_response(500, "GROQ_API_KEY not configured. Cannot transcribe.")

    try:
        client = Groq(api_key=groq_key)
        transcription = client.audio.transcriptions.create(
            file=(file.filename, contents),
            model="whisper-large-v3-turbo",
            language="en",
            temperature=0.0,
            response_format="verbose_json",
        )
        transcript_text = transcription.text
        duration = getattr(transcription, "duration", 0)
    except Exception as exc:
        return _error_response(500, f"Transcription failed: {exc}")

    if not transcript_text or not transcript_text.strip():
        return _error_response(422, "Transcription returned empty text.")

    # Run compliance scan
    try:
        dispatch = {
            "quick": lambda: quick_scan_impl(transcript_text),
            "full": lambda: full_analysis_impl(transcript_text),
            "deep": lambda: deep_review_impl(transcript_text),
        }
        handler = dispatch.get(detail_level, dispatch["full"])
        result = handler()

        elapsed = round(time.time() - start, 2)

        report = result.get("report", {})
        readable = result.get("content", [{}])[0].get("text", "")
        html_report = result.get("html_report", "")
        _record_scan(
            scan_type="upload",
            content_preview=f"[{file.filename}] {transcript_text[:80]}",
            detail_level=detail_level,
            report=report,
            html_report=html_report,
        )

        return JSONResponse(content={
            "status": result.get("status", "success"),
            "detail_level": detail_level,
            "report": report,
            "readable": readable,
            "compliance_score": report.get("compliance_score", None),
            "upload": {
                "filename": file.filename,
                "size_bytes": len(contents),
                "duration_seconds": duration or 0,
                "transcript_length": len(transcript_text),
            },
            "transcript_preview": transcript_text[:500],
            "elapsed_seconds": elapsed,
        })

    except Exception as exc:
        _record_scan(
            scan_type="upload",
            content_preview=f"[{file.filename}]",
            detail_level=detail_level,
            report={},
            status="error",
            html_report="",
        )
        return _error_response(500, f"Internal server error: {exc}")


class _HTMLTextExtractor(HTMLParser):
    """Minimal HTML-to-text extractor."""
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []
    def handle_data(self, data: str):
        self._parts.append(data)
    def get_text(self) -> str:
        return " ".join(self._parts)


@app.post("/api/scan-url")
async def scan_url(request: Request, body: ScanUrlRequest) -> JSONResponse:
    """Fetch a webpage, strip HTML, and scan the text for compliance issues."""
    # Rate limiting
    if not _check_rate_limit(_get_client_ip(request)):
        return _error_response(429, "Rate limit exceeded. Max 30 requests per minute.")

    # Input validation
    url = body.url.strip()
    if not url:
        return _error_response(400, "URL must not be empty.")
    if len(url) > _MAX_URL_LENGTH:
        return _error_response(400, f"URL too long. Maximum {_MAX_URL_LENGTH} characters.")

    start = time.time()

    # 1. Fetch webpage
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ComplianceScanner/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw_html = resp.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return _error_response(422, f"Failed to fetch URL: {exc}")

    # 2. Strip HTML tags to plain text, truncate to 8000 chars
    extractor = _HTMLTextExtractor()
    extractor.feed(raw_html)
    plain_text = extractor.get_text()[:8000]

    if not plain_text.strip():
        return _error_response(422, "No text content extracted from URL.")

    # 3. Run compliance scan
    try:
        dispatch = {
            "quick": lambda: quick_scan_impl(plain_text),
            "full": lambda: full_analysis_impl(plain_text),
            "deep": lambda: deep_review_impl(plain_text),
        }
        handler = dispatch.get(body.detail_level, dispatch["quick"])
        result = handler()
        elapsed = round(time.time() - start, 2)

        report = result.get("report", {})
        readable = result.get("content", [{}])[0].get("text", "")
        html_report = result.get("html_report", "")
        _record_scan(
            scan_type="url",
            content_preview=url,
            detail_level=body.detail_level,
            report=report,
            status="completed" if result.get("status") == "success" else "error",
            html_report=html_report,
        )

        return JSONResponse(content={
            "status": result.get("status", "success"),
            "source_url": url,
            "detail_level": body.detail_level,
            "report": report,
            "readable": readable,
            "compliance_score": report.get("compliance_score", None),
            "content_length": len(plain_text),
            "elapsed_seconds": elapsed,
        })
    except Exception as exc:
        _record_scan(
            scan_type="url",
            content_preview=url,
            detail_level=body.detail_level,
            report={},
            status="error",
            html_report="",
        )
        return _error_response(500, f"Internal server error: {exc}")


@app.post("/api/webhook/register")
async def webhook_register(body: WebhookRegisterRequest) -> JSONResponse:
    """Register a webhook URL to receive scan results."""
    try:
        url = body.url.strip()
        if not url:
            return _error_response(400, "Webhook URL must not be empty.")
        if len(url) > _MAX_URL_LENGTH:
            return _error_response(400, f"URL too long. Maximum {_MAX_URL_LENGTH} characters.")
        if url not in _webhooks:
            _webhooks.append(url)
        return JSONResponse(content={"status": "registered", "url": url})
    except Exception as exc:
        return _error_response(500, f"Internal server error: {exc}")


@app.get("/api/webhook/list")
async def webhook_list() -> JSONResponse:
    """List all registered webhook URLs."""
    try:
        return JSONResponse(content={"webhooks": _webhooks})
    except Exception as exc:
        return _error_response(500, f"Internal server error: {exc}")


@app.get("/api/report/{scan_id}")
async def get_report(scan_id: str):
    """Return the stored HTML compliance report for a given scan ID."""
    try:
        for entry in _scan_history:
            if entry["id"] == scan_id:
                html = entry.get("html_report", "")
                if not html:
                    return _error_response(404, "No HTML report stored for this scan")
                return HTMLResponse(content=html)
        return _error_response(404, f"Scan {scan_id} not found")
    except Exception as exc:
        return _error_response(500, f"Internal server error: {exc}")


@app.get("/api/badge")
async def badge():
    """Returns an SVG badge showing total scans."""
    try:
        avg = round(sum(_risk_scores) / len(_risk_scores), 1) if _risk_scores else 0
        color = "#10b981" if avg < 4 else "#f59e0b" if avg < 7 else "#ef4444"
        label = "ComplianceShield"
        value = f"{_total_scans} scans"
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="220" height="20">
          <rect width="130" height="20" fill="#555" rx="3"/>
          <rect x="130" width="90" height="20" fill="{color}" rx="3"/>
          <rect width="220" height="20" rx="3" fill="url(#g)"/>
          <text x="65" y="14" fill="#fff" text-anchor="middle" font-family="Verdana" font-size="11">{label}</text>
          <text x="175" y="14" fill="#fff" text-anchor="middle" font-family="Verdana" font-size="11">{value}</text>
        </svg>'''
        from fastapi.responses import Response
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as exc:
        return _error_response(500, f"Internal server error: {exc}")


@app.get("/api/badge/risk")
async def badge_risk():
    """Returns an SVG badge showing average risk level with color coding."""
    try:
        avg = round(sum(_risk_scores) / len(_risk_scores), 1) if _risk_scores else 0
        color = "#10b981" if avg < 4 else "#f59e0b" if avg < 7 else "#ef4444"
        label = "Avg Risk"
        value = f"{avg}/10"
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="20">
          <rect width="80" height="20" fill="#555" rx="3"/>
          <rect x="80" width="80" height="20" fill="{color}" rx="3"/>
          <rect width="160" height="20" rx="3" fill="url(#g)"/>
          <text x="40" y="14" fill="#fff" text-anchor="middle" font-family="Verdana" font-size="11">{label}</text>
          <text x="120" y="14" fill="#fff" text-anchor="middle" font-family="Verdana" font-size="11">{value}</text>
        </svg>'''
        from fastapi.responses import Response
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as exc:
        return _error_response(500, f"Internal server error: {exc}")


@app.get("/.well-known/agent.json")
async def proxy_agent_card():
    """Proxy the A2A agent card from port 9000 for frontend pages."""
    import urllib.request
    try:
        with urllib.request.urlopen("http://localhost:9000/.well-known/agent.json", timeout=3) as resp:
            data = resp.read()
        return JSONResponse(content=json.loads(data))
    except Exception:
        return _error_response(502, "A2A agent not reachable on port 9000")


@app.get("/{full_path:path}")
async def serve_landing(request: Request, full_path: str):
    """Serve static files from the landing/ directory.

    GET / serves landing/index.html. Any other path is resolved
    relative to the landing/ directory (CSS, JS, images, etc.).
    """
    try:
        if not full_path or full_path == "/":
            full_path = "index.html"

        file_path = _LANDING_DIR / full_path

        if file_path.is_file():
            return FileResponse(file_path)

        # Fallback: serve 404 page if available, else JSON error
        notfound = _LANDING_DIR / "404.html"
        if notfound.is_file():
            return FileResponse(notfound, status_code=404)

        return _error_response(404, f"Not found: {full_path}")
    except Exception as exc:
        return _error_response(500, f"Internal server error: {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Run the demo web server."""
    print(f"\n{'=' * 60}")
    print(f"  COMPLIANCE CHECKER — DEMO")
    print(f"  http://localhost:{DEMO_PORT}")
    print(f"{'=' * 60}")
    print(f"\n  Landing page : landing/index.html")
    print(f"  API docs     : http://localhost:{DEMO_PORT}/docs")
    print(f"\n  Endpoints:")
    print(f"    GET  /               — Landing page")
    print(f"    POST /api/scan       — Scan text content")
    print(f"    POST /api/scan-video — Scan YouTube video")
    print(f"    POST /api/scan-url   — Fetch & scan a webpage URL")
    print(f"    POST /api/scan-upload— Upload audio/video, transcribe + scan")
    print(f"    POST /api/scan-batch — Scan multiple texts")
    print(f"    GET  /api/stats      — Usage statistics")
    print(f"    GET  /api/history    — Scan history (last 50)")
    print(f"    GET  /api/health     — Health check")
    print()

    uvicorn.run(app, host="0.0.0.0", port=DEMO_PORT)


if __name__ == "__main__":
    main()
