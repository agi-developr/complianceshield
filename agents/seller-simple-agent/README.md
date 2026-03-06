# ComplianceShield

**AI-Powered Legal Compliance for Content Creators**

> Your content. Legally clear.

Built at the [Nevermined Autonomous Business Hackathon](https://nevermined.io) | March 5-6, 2026 | AWS Loft, San Francisco

---

## What It Does

ComplianceShield scans content (YouTube videos, text, audio, URLs) for legal compliance issues across **8 regulatory frameworks**: FTC, FDA, SEC, FINRA, COPPA, CAN-SPAM, CCPA, and GDPR.

Every issue includes the **exact problematic text**, the **specific regulation** it violates, a **link to the official law**, and a **recommended fix**.

```
Input:  "This supplement cures cancer! Use code HEALTH50 for 50% off!"
Output: 3 HIGH-risk issues (FDA, FTC, Health Claims) — Score: 5/100
```

## Three Protocols, One Engine

| Protocol | Port | For | How It Works |
|----------|------|-----|-------------|
| **A2A** (Agent-to-Agent) | 9000 | AI agents | Agent card discovery + x402 paid JSON-RPC |
| **MCP** (Model Context Protocol) | 3000 | Claude Desktop, Cursor | 4 payment-gated tools |
| **REST** (Web Demo) | 8080 | Humans | Free scanning, dashboard, 14 API endpoints |

## Quick Start

```bash
cd agents/seller-simple-agent
poetry install
cp .env.example .env
# Set: NVM_API_KEY, NVM_PLAN_ID, NVM_AGENT_ID, ANTHROPIC_API_KEY

# Start all services
bash ../../restart-all.sh

# Public access for other agents
ngrok http 9000
```

## Pricing

| Tool | Credits | Description |
|------|---------|-------------|
| `quick_scan` | 1 | Fast scan for obvious issues |
| `full_analysis` | 5 | Detailed per-section compliance report |
| `scan_video` | 8 | YouTube URL to compliance report |
| `deep_review` | 10 | Full analysis + legal citations + rewrites + penalties |

## Architecture

```
  A2A (9000)  ──┐
  MCP (3000)  ──┼──> Compliance Engine (Claude Haiku 4.5)
  REST (8080) ──┘         │
                    ┌─────┼──────┐
                    │     │      │
              YouTube  Groq    25+ Regulation
              Transcript Whisper  Link Resolver
              API      (Audio)   (Official URLs)
                          │
                    Nevermined x402
                    Payment Layer
```

## Features

- 4 input modes: YouTube URL, text, audio/video upload, webpage URL
- Batch scanning (up to 20 items)
- Animated compliance score gauge (0-100)
- Professional HTML reports with clickable regulation links
- SVG badges for creator websites
- Webhook notifications
- Telegram bot integration
- 10-page product frontend (landing, dashboard, API docs, pricing, etc.)
- Rate limiting (30 req/min)
- Input validation on all endpoints

## Live Endpoints

| Endpoint | URL |
|----------|-----|
| Product Page | http://localhost:8080 |
| Dashboard | http://localhost:8080/dashboard.html |
| API Docs | http://localhost:8080/api-docs.html |
| Agent Card | http://localhost:9000/.well-known/agent.json |
| MCP Server | http://localhost:3000/mcp |
| Buyer Agent | http://localhost:8000 |

## API Examples

```bash
# Text scan
curl -X POST http://localhost:8080/api/scan \
  -H "Content-Type: application/json" \
  -d '{"content": "Buy now! Guaranteed results!", "detail_level": "quick"}'

# YouTube video scan
curl -X POST http://localhost:8080/api/scan-video \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://youtube.com/watch?v=VIDEO_ID", "detail_level": "full"}'

# Stats
curl http://localhost:8080/api/stats
```

## Regulation Coverage

25+ regulations mapped to official sources:

| Category | Regulations |
|----------|------------|
| FTC / Advertising | 16 CFR Part 255, FTC Act Section 5 |
| Health / FDA | 21 CFR Part 101, 21 CFR Part 343, FDCA |
| Financial / SEC | SEC Rule 10b-5, FINRA Rule 2210 |
| Privacy | COPPA, CAN-SPAM, HIPAA, CCPA, GDPR, FERPA |
| IP / Copyright | Lanham Act, DMCA |
| Platform | YouTube, Instagram, TikTok guidelines |

## Tech Stack

Python 3.12 | FastAPI | Claude Haiku 4.5 | Groq Whisper | Strands SDK | Nevermined payments-py | a2a-python | ngrok

---

**ComplianceShield — Stop getting fined. Start creating safely.**
