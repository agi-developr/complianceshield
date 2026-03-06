# ComplianceShield

### AI-Powered Legal Compliance for the Creator Economy

**Nevermined Autonomous Business Hackathon | March 5-6, 2026 | AWS Loft, San Francisco**

---

## The Problem

Content creators face a $337M enforcement problem. The FTC returned that amount to consumers from disclosure violations in 2024 alone. A single non-compliant YouTube video triggers fines starting at **$53,088 per violation** under 2025 penalty rates. The FTC put 670 companies on notice in 2023, and class-action lawsuits against creators (Celsius, Shein) are accelerating.

**The alternatives are broken:**

| Option | Cost | Problem |
|--------|------|---------|
| Hire a lawyer | $313/hr average | A single content review costs $500-1,500. Does not scale. |
| Enterprise platforms (CreatorIQ) | $30-90K/year | Built for brands with legal teams, not individual creators. |
| Manual checklists | Free | Error-prone, cannot keep up with regulatory changes. |
| Do nothing | $0 upfront | One FTC notice and you are done. |

**There is no affordable, automated tool that scans creator content for legal compliance before publishing.** ComplianceShield fills that gap.

---

## What We Built

ComplianceShield is an AI-powered compliance engine that scans content (YouTube videos, text scripts, audio/video files) against FTC, FDA, SEC, FINRA, COPPA, CAN-SPAM, CCPA, and GDPR regulations. It returns structured reports with specific law citations, links to official regulatory sources, risk levels, and recommended fixes.

**What makes it different**: ComplianceShield is not a product. It is **infrastructure**. It speaks three protocols -- any human, any AI agent, any developer tool can discover it, pay for it, and use it without custom integration.

### Input Modes

- **YouTube URL** -- Extracts transcript automatically, runs compliance analysis
- **Text content** -- Scripts, social media posts, podcast transcripts, blog drafts
- **Audio/Video upload** -- Transcribes via Groq Whisper (whisper-large-v3-turbo), then scans

### Output

- Structured JSON compliance report with per-issue risk levels (HIGH / MEDIUM / LOW)
- Exact quotes of problematic text
- Specific regulation citations (e.g., "16 CFR Part 255", "SEC Rule 10b-5")
- Links to official regulation sources (eCFR, law.cornell.edu, FTC.gov)
- Recommended fixes and compliant rewrites
- Beautiful HTML reports ready to print or share
- Penalty estimates on deep review tier

---

## Architecture

```
                                    ComplianceShield
    ┌──────────────────────────────────────────────────────────────────────┐
    │                                                                      │
    │  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐ │
    │  │   A2A Server │   │  MCP Server  │   │     REST Demo Server     │ │
    │  │   Port 9000  │   │  Port 3000   │   │       Port 8080          │ │
    │  │              │   │              │   │                          │ │
    │  │  JSON-RPC    │   │  4 Tools     │   │  Landing Page            │ │
    │  │  Agent Card  │   │  Claude/     │   │  Dashboard               │ │
    │  │  Nevermined  │   │  Cursor/     │   │  API Docs                │ │
    │  │  x402 Payments│  │  Any MCP     │   │  Free Scanning           │ │
    │  │              │   │  Client      │   │  Stats + History         │ │
    │  └──────┬───────┘   └──────┬───────┘   └────────────┬─────────────┘ │
    │         │                  │                         │               │
    │         └──────────────────┼─────────────────────────┘               │
    │                            │                                         │
    │                   ┌────────▼────────┐                                │
    │                   │  Compliance     │                                │
    │                   │  Engine         │                                │
    │                   │                 │                                │
    │                   │  Claude Haiku   │                                │
    │                   │  4.5            │                                │
    │                   │  (Analysis)     │                                │
    │                   └────────┬────────┘                                │
    │                            │                                         │
    │              ┌─────────────┼─────────────┐                           │
    │              │             │             │                           │
    │     ┌────────▼──────┐ ┌───▼────────┐ ┌──▼──────────────┐           │
    │     │  YouTube      │ │  Groq      │ │  Regulation     │           │
    │     │  Transcript   │ │  Whisper   │ │  Link Resolver  │           │
    │     │  API          │ │  (Audio)   │ │  (25+ URLs)     │           │
    │     └───────────────┘ └────────────┘ └─────────────────┘           │
    │                                                                      │
    └──────────────────────────────────────────────────────────────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │    Nevermined      │
                          │    Payments SDK    │
                          │                   │
                          │  x402 Protocol    │
                          │  Credit Plans     │
                          │  Token Settlement │
                          │  Sandbox Network  │
                          └───────────────────┘
```

### Protocol Breakdown

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THREE PROTOCOLS, ONE ENGINE                         │
├────────────────────┬────────────────────┬───────────────────────────────────┤
│                    │                    │                                   │
│   A2A (Agent)      │   MCP (Developer)  │   REST (Product)                 │
│                    │                    │                                   │
│   Any AI agent     │   Claude Desktop   │   Content creators               │
│   discovers via    │   Cursor, or any   │   scan videos and                │
│   /.well-known/    │   MCP client       │   text content                   │
│   agent.json       │   connects to      │   through a web                  │
│                    │   4 paid tools      │   interface                      │
│   Pays with x402   │                    │                                   │
│   token in header  │   Credits deducted │   Free tier for                  │
│                    │   per tool call     │   demo / product                 │
│   JSON-RPC msgs    │                    │   usage                          │
│   with Nevermined  │   quick_scan: 1cr  │                                   │
│   settlement       │   full_analysis:5  │   POST /api/scan                 │
│                    │   scan_video: 8cr  │   POST /api/scan-video           │
│   Port 9000        │   deep_review: 10  │   POST /api/scan-upload          │
│   (ngrok public)   │                    │   POST /api/scan-batch           │
│                    │   Port 3000        │   GET  /api/stats                │
│                    │                    │   GET  /api/history              │
│                    │                    │                                   │
│                    │                    │   Port 8080                      │
│                    │                    │                                   │
├────────────────────┴────────────────────┴───────────────────────────────────┤
│                                                                             │
│              Nevermined x402 Payment Layer (Sandbox Network)                │
│              Plan registered  ·  100 credits allocated                      │
│              2 paid A2A transactions completed (98 remaining)               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Payment Flow (A2A)

```
  Buyer Agent                                      ComplianceShield
  ──────────                                       ────────────────

  1. GET /.well-known/agent.json ────────────────> Agent card returned
     (discovers capabilities + pricing)             with Nevermined extension

  2. Acquire x402 token from Nevermined ─────────> (off-chain settlement)
     (deducts credits from buyer's plan)

  3. POST / (JSON-RPC message) ──────────────────> PaymentsRequestHandler
     Header: payment-signature: <x402-token>        validates token
                                                     ↓
                                                   StrandsA2AExecutor
                                                     runs compliance scan
                                                     ↓
  4. <───────────────────────────────── 200 OK      Returns report +
     TaskStatusUpdateEvent with                     settles credits via
     compliance report + creditsUsed                Nevermined SDK
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Runtime** | Python 3.12 + FastAPI | HTTP servers, async event handling |
| **AI Analysis** | Anthropic Claude (claude-haiku-4-5) | Compliance analysis engine |
| **Transcription** | Groq Whisper (whisper-large-v3-turbo) | Audio/video file transcription |
| **YouTube** | youtube-transcript-api v1.x | YouTube transcript extraction |
| **Agent Framework** | AWS Strands SDK | Tool orchestration, agent creation |
| **A2A Protocol** | a2a-python SDK | Agent-to-agent JSON-RPC server |
| **MCP Protocol** | Nevermined PaymentsMCP | MCP server with payment-gated tools |
| **Payments** | Nevermined payments-py SDK | x402 protocol, credit plans, settlement |
| **Frontend** | Static HTML/CSS/JS | Landing page, dashboard, API docs |
| **Tunnel** | ngrok | Public A2A endpoint for cross-team discovery |

---

## Pricing Model

| Tier | Credits | What You Get |
|------|---------|--------------|
| `quick_scan` | 1 credit | Fast scan for obvious issues -- FTC disclosure, basic health claims |
| `full_analysis` | 5 credits | Per-section compliance report with risk scores across all categories |
| `scan_video` | 8 credits | YouTube URL to compliance report (transcript extraction + analysis) |
| `deep_review` | 10 credits | Full analysis + specific legal citations + compliant rewrites + penalty estimates |

**Hackathon stats**: 100 credits allocated on Nevermined sandbox. 2 paid A2A transactions completed. 98 credits remaining.

---

## Regulation Coverage

ComplianceShield maps 25+ regulation identifiers to official government and legal sources:

| Category | Regulations Covered | Sources |
|----------|-------------------|---------|
| **FTC / Advertising** | 16 CFR Part 255 (Endorsement Guides), FTC Act Section 5 | ecfr.gov, law.cornell.edu |
| **Health / FDA** | 21 CFR Part 101 (Food Labeling), 21 CFR Part 343 (OTC Drugs), FDCA | ecfr.gov, law.cornell.edu |
| **Financial / SEC** | SEC Rule 10b-5, FINRA Rule 2210, Investment Advisers Act | law.cornell.edu, finra.org |
| **Privacy** | COPPA, CAN-SPAM, HIPAA, CCPA, GDPR, FERPA | law.cornell.edu, hhs.gov, oag.ca.gov, gdpr-info.eu |
| **IP / Copyright** | Lanham Act, DMCA | law.cornell.edu |
| **Platform** | YouTube, Instagram, TikTok community guidelines | youtube.com, instagram.com, tiktok.com |

Every issue in a compliance report includes a clickable link to the official regulation source. No hallucinated citations.

---

## Features Implemented

### Core Compliance Engine
- [x] YouTube video URL scanning with automatic transcript extraction
- [x] Text content scanning (scripts, posts, transcripts, drafts)
- [x] Audio/video file upload with Groq Whisper transcription (25MB limit, 10 formats)
- [x] Webpage URL scanning (fetches page, strips HTML, runs compliance analysis)
- [x] Batch scanning endpoint (up to 20 items per request)
- [x] Three analysis tiers: quick scan, full analysis, deep review
- [x] AI-generated compliance scores (0-100) with color-coded risk visualization
- [x] Real regulation citations with links to official law sources (25+ mapped URLs)
- [x] Professional HTML compliance reports (print-ready, shareable via unique URL)
- [x] Animated circular score gauge with color-coded risk visualization

### Protocols & Payments
- [x] A2A server with agent card discovery and Nevermined payment settlement
- [x] MCP server with 4 payment-gated tools for Claude Desktop / Cursor
- [x] REST API with 14 endpoints (scan, stats, history, badges, webhooks, reports)
- [x] x402 payment protocol with credit-based pricing
- [x] Completed paid A2A transactions on Nevermined sandbox

### Product & Frontend (10 Pages)
- [x] Landing page with 4 input modes (video, text, upload, URL)
- [x] Live dashboard with Chart.js donut charts, agent health monitoring
- [x] Comprehensive API documentation with tabbed code examples (cURL, Python, JS)
- [x] Pricing page with 3 tiers, annual toggle, feature comparison table
- [x] Getting started guide with 6 sections (creators, developers, AI agents)
- [x] Regulations reference page with 27 regulation cards across 7 categories
- [x] Login page with particle animations and social auth
- [x] System status page with live health checks and changelog
- [x] Embeddable badge/widget page for creator trust signals
- [x] 404 error page with animated gradient

### Integrations & Developer Tools
- [x] Embeddable SVG badges (scan count + risk level) for creator websites
- [x] Webhook notifications (register URL, receive scan results automatically)
- [x] Telegram bot (commands: /scan, /scanfull, /video + auto-scan on text)
- [x] Claude Desktop MCP integration configured
- [x] ngrok tunnel for public A2A access across hackathon teams
- [x] Multiple LLM provider support (Anthropic, OpenAI, AWS Bedrock)

---

## Live Demo URLs

| Endpoint | URL | Purpose |
|----------|-----|---------|
| Product Landing | http://localhost:8080 | Main product page with 4-mode scanner |
| Dashboard | http://localhost:8080/dashboard.html | Real-time stats, Chart.js charts, agent health |
| API Documentation | http://localhost:8080/api-docs.html | Interactive API reference with code examples |
| Pricing | http://localhost:8080/pricing.html | 3 tiers, feature comparison, FAQ |
| Getting Started | http://localhost:8080/getting-started.html | Onboarding for creators, devs, AI agents |
| Regulations | http://localhost:8080/regulations.html | 27 regulation cards with official links |
| System Status | http://localhost:8080/status.html | Live health checks, changelog |
| Embed Badges | http://localhost:8080/embed.html | Embeddable trust badges for creators |
| A2A Agent (public) | https://candelaria-fierce-ingeniously.ngrok-free.dev | Agent discovery + paid scanning |
| MCP Server | http://localhost:3000/mcp | Connect from Claude Desktop / Cursor |
| Agent Card | https://candelaria-fierce-ingeniously.ngrok-free.dev/.well-known/agent.json | A2A agent metadata |
| Scan Badge (SVG) | http://localhost:8080/api/badge | Embeddable scan count badge |
| Risk Badge (SVG) | http://localhost:8080/api/badge/risk | Embeddable risk level badge |

---

## Business Model

### Revenue Streams

| Channel | Model | Target Customer |
|---------|-------|-----------------|
| **SaaS (Creator)** | $29/month unlimited scans | Individual creators (10K-1M subscribers) |
| **SaaS (Agency)** | $99/month + team seats | Talent agencies, MCNs |
| **API Credits** | Pay-per-scan via Nevermined | Developer integrations |
| **Agent Economy** | x402 micropayments | AI agents purchasing scans autonomously |
| **Enterprise** | $299/month white-label | Brands, legal teams, platforms |

### Market Opportunity

| Metric | Value |
|--------|-------|
| Global content creators | 207-303 million (DemandSage 2025) |
| Creator economy market size | $178-250 billion (2025) |
| Creator economy CAGR | 21-23% to $1.35T by 2033 |
| Compliance software market | $36-60 billion (2025) |
| Machine-customer economy by 2030 | $30T (Gartner) |
| YouTube channels 10K-1M subs (beachhead) | ~2 million |

**Unit economics**: AI scan cost ~$0.02-0.05 per analysis. At $29/month with average usage, gross margin exceeds 95%.

**1% of beachhead** = 20,000 paying users x $29/month = **$6.96M ARR**.

### Roadmap

| Phase | Timeline | Focus |
|-------|----------|-------|
| Launch | Months 1-3 | Chrome extension for YouTube Studio, SEO content marketing |
| Expand | Months 3-6 | MCP marketplace distribution, A2A agent network, agency API |
| Scale | Months 6-12 | Instagram, TikTok, podcast scanning. UK ASA, EU DSA rule engines |
| Platform | Year 2 | White-label for platforms, MCN partnerships, jurisdiction engine |

---

## Hackathon Achievements

- Built a working 3-protocol compliance service (A2A, MCP, REST) in 48 hours
- Completed paid A2A transactions through Nevermined x402 protocol
- Registered payment plan on Nevermined sandbox with credit-based pricing
- Integrated 3 external AI services (Claude Haiku 4.5, Groq Whisper, YouTube Transcript API)
- Mapped 25+ regulations to official government sources (no hallucinated citations)
- AI-generated compliance scores (0-100) with animated circular gauge visualization
- Built 10-page product frontend (landing, dashboard, API docs, pricing, getting-started, regulations, login, status, embed, 404)
- 14 API endpoints including scan, stats, badges, webhooks, and shareable reports
- Telegram bot integration for mobile compliance scanning
- Embeddable SVG badges for creator trust signals
- Webhook notification system for automated compliance pipelines
- Deployed public A2A endpoint via ngrok for cross-team agent discovery

---

## Prize Categories

| Prize | Category | Why ComplianceShield |
|-------|----------|---------------------|
| **Best Seller Agent** ($1K) | Agent that sells data/services with Nevermined payments | 4 paid tools, tiered pricing, completed A2A transactions, x402 settlement |
| **Ability.ai Business Automation** ($2K) | Best business automation use case | Automates $313/hr legal review work. 95% gross margin SaaS. Real market need. |
| **Best Global** ($3K) | Best overall project | 3 protocols, working product, real business model, massive TAM, deployed and transacting |

---

## Running the Project

```bash
# Clone and install
cd agents/seller-simple-agent
poetry install

# Configure environment
cp .env.example .env
# Set: NVM_API_KEY, NVM_PLAN_ID, NVM_AGENT_ID, ANTHROPIC_API_KEY, GROQ_API_KEY

# Terminal 1: A2A Agent (port 9000)
poetry run python -m src.agent_a2a

# Terminal 2: MCP Server (port 3000)
poetry run python -m src.mcp_server

# Terminal 3: Product Demo (port 8080)
poetry run python -m src.web_demo

# Terminal 4: Public tunnel
ngrok http 9000
```

---

## Team

Built at the Nevermined Autonomous Business Hackathon, AWS Loft SF.

**Three protocols. One compliance engine. Zero FTC fines.**

---

*ComplianceShield -- Stop getting fined. Start creating safely.*
