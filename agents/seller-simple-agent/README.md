# Seller Simple Agent — ComplianceShield

**AI-powered legal compliance service** with Nevermined x402 payment integration. Runs as both a REST API (WebDemo) and A2A agent with automatic payment settlement.

This is the core service of ComplianceShield, providing:
- **WebDemo** (port 8080): Interactive landing page + free REST scanning API
- **A2A Agent** (port 9000): Nevermined-integrated agent for B2B compliance services
- **Payment Integration**: Automatic credit settlement via Nevermined x402 protocol

> Built at the [Nevermined Autonomous Business Hackathon](https://nevermined.io) | March 5-6, 2026 | AWS Loft, San Francisco

## 🚀 Quick Start

### Prerequisites

```bash
python3 --version      # 3.10+
poetry --version       # Required
```

### Start WebDemo (REST API)

```bash
cd /Users/ilaprihodko/hackathon-compliance/agents/seller-simple-agent
poetry install
poetry run web-demo
# Runs on http://localhost:8080
```

### Start A2A Agent (Nevermined)

In a separate terminal:

```bash
cd /Users/ilaprihodko/hackathon-compliance/agents/seller-simple-agent
poetry run agent-a2a --port 9000 --buyer-url http://localhost:8000
# Runs on http://localhost:9000
```

### Test Both Services

```bash
# Test WebDemo REST API
curl -X POST http://localhost:8080/api/scan \
  -H "Content-Type: application/json" \
  -d '{"content": "Our supplement cures cancer!", "detail_level": "quick"}'

# Check A2A agent discovery
curl http://localhost:9000/.well-known/agent.json | jq
```

## 📋 What Gets Shipped

### Services

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| **WebDemo** | 8080 | REST (JSON) | Public-facing landing page + free API |
| **A2A Agent** | 9000 | JSON-RPC + x402 | B2B agent with Nevermined payments |

### 4 Core Compliance Scanning Modes

1. **Quick Scan** (1-2 sec, 1 credit)
   - Basic risk assessment (LOW/MEDIUM/HIGH)
   - Identifies violation types
   - Compliance score

2. **Full Analysis** (3-5 sec, 5 credits)
   - Per-claim risk scoring
   - Specific regulation citations
   - Issue severity breakdown

3. **Deep Review** (5-10 sec, 10 credits)
   - Comprehensive legal analysis
   - Rewrite suggestions
   - Citation references

4. **Video Scan** (2-4 sec, 8 credits)
   - YouTube transcript analysis
   - Timestamps of violations
   - Speaker attribution

### Compliance Categories Checked

- **FTC** (Federal Trade Commission)
  - Unsubstantiated health claims
  - Deceptive endorsements
  - Missing disclaimers

- **FDA** (Food & Drug Administration)
  - Disease cure claims
  - Off-label drug use
  - Supplement structure/function rules

- **SEC** (Securities & Exchange Commission)
  - Unregistered investment claims
  - Pump & dump language
  - Insider trading hints

- **Privacy & Data**
  - GDPR/CCPA violations
  - Unauthorized tracking
  - PII disclosure

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│  Seller Simple Agent                           │
├─────────────────────────────────────────────────┤
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │  FastAPI Server                          │ │
│  │  - CORS enabled                          │ │
│  │  - Rate limiting (30 req/min per IP)     │ │
│  │  - Request validation                    │ │
│  └──────────┬───────────────────────────────┘ │
│             │                                  │
│    ┌────────┴────────┐                        │
│    │                 │                        │
│    ▼                 ▼                        │
│  ┌──────────┐   ┌──────────┐                │
│  │ WebDemo  │   │ A2A      │                │
│  │ (8080)   │   │ (9000)   │                │
│  │ REST API │   │ JSON-RPC │                │
│  └────┬─────┘   └────┬─────┘                │
│       │              │                       │
│       └──────┬───────┘                       │
│              ▼                               │
│    ┌──────────────────┐                     │
│    │ Claude API       │                     │
│    │ (LLM)            │                     │
│    │ - Compliance     │                     │
│    │   analysis       │                     │
│    │ - Rule checking  │                     │
│    │ - Suggestions    │                     │
│    └──────────────────┘                     │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │ Payment Handler (A2A only)           │  │
│  │ - Validates Nevermined tokens        │  │
│  │ - Deducts credits                    │  │
│  │ - Settles transactions               │  │
│  └──────────────────────────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

## 🔌 API Reference

### REST API (WebDemo)

**Base URL**: `http://localhost:8080`
**Authentication**: None (demo)

#### POST /api/scan

Scan content for compliance issues.

**Request**:
```json
{
  "content": "Your marketing copy or script here",
  "detail_level": "quick|full|deep"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "detail_level": "quick",
  "report": {
    "overall_risk": "LOW|MEDIUM|HIGH",
    "summary": "Human-readable summary",
    "issues": [
      {
        "type": "FTC|FDA|SEC|PRIVACY",
        "severity": "LOW|MEDIUM|HIGH",
        "claim": "The problematic text",
        "rule": "Applicable regulation",
        "suggestion": "How to fix it"
      }
    ],
    "compliance_score": 95,
    "safe_sections": "What passed"
  },
  "report_id": "33d89058",
  "elapsed_seconds": 2.68,
  "readable": "Formatted text report"
}
```

**Example**:
```bash
curl -X POST http://localhost:8080/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Try our miracle weight loss supplement! Lose 50 lbs in 30 days!",
    "detail_level": "full"
  }'
```

#### GET /

Landing page (HTML).

Response: Beautiful product landing page with features, pricing, demo.

#### GET /api/health

Health check.

**Response**:
```json
{
  "status": "ok",
  "service": "compliance-scanner",
  "timestamp": "2026-03-06T22:14:10.150661Z"
}
```

### A2A Agent API

**Base URL**: `http://localhost:9000`
**Protocol**: JSON-RPC 2.0
**Authentication**: Nevermined x402 (payment-signature header)

#### GET /.well-known/agent.json

Agent discovery endpoint.

**Response**:
```json
{
  "name": "Compliance Checker Agent",
  "description": "AI-powered legal compliance checker for content creators",
  "url": "http://localhost:9000",
  "version": "0.1.0",
  "skills": [
    {
      "id": "quick_scan",
      "name": "Quick Compliance Scan",
      "description": "Quick scan for legal compliance issues. Costs 1 credit.",
      "tags": ["compliance", "legal", "quick"]
    },
    {
      "id": "full_analysis",
      "name": "Full Compliance Analysis",
      "description": "Detailed analysis with per-claim scores. Costs 5 credits.",
      "tags": ["compliance", "legal", "detailed"]
    },
    {
      "id": "deep_review",
      "name": "Deep Compliance Review",
      "description": "Comprehensive legal review with suggestions. Costs 10 credits.",
      "tags": ["compliance", "legal", "comprehensive"]
    },
    {
      "id": "scan_video",
      "name": "YouTube Video Compliance Scan",
      "description": "Analyze video transcripts for compliance. Costs 8 credits.",
      "tags": ["video", "compliance", "youtube"]
    }
  ],
  "pricing": "Credits vary: quick_scan=1, full_analysis=5, deep_review=10, scan_video=8"
}
```

#### POST / (JSON-RPC)

Submit compliance request with payment.

**Headers**:
```
Content-Type: application/json
payment-signature: {Nevermined_access_token}
```

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "quick_scan",
  "params": {
    "content": "Your content here"
  },
  "id": 1
}
```

**Response** (200 OK):
```json
{
  "jsonrpc": "2.0",
  "result": {
    "overall_risk": "LOW",
    "compliance_score": 95,
    "issues": [],
    "summary": "No violations detected",
    "report_id": "a1b2c3d4"
  },
  "id": 1
}
```

**Error** (402 Payment Required):
```json
{
  "error": {
    "code": -32001,
    "message": "Missing payment-signature header"
  }
}
```

## 💳 Payment Flow (x402)

```
Buyer Agent                              Seller Agent (This)
     │                                        │
     ├─ GET /.well-known/agent.json          │
     │────────────────────────────────────────>
     │                                        │
     │   <────────────────────────────────────┤
     │     Agent metadata + pricing           │
     │                                        │
     ├─ Get Nevermined access token          │
     │ (via nevermined.app API)              │
     │                                        │
     ├─ POST / (JSON-RPC + payment-signature)│
     │────────────────────────────────────────>
     │                                        │
     │   PaymentsRequestHandler validates     │
     │   token against Nevermined service     │
     │                                        │
     │   Strands agent executes quick_scan   │
     │   (1 credit deducted)                 │
     │                                        │
     │   <────────────────────────────────────┤
     │     Result + settled transaction      │
     │                                        │
```

### Setup Nevermined (One-Time)

1. Create account at https://nevermined.app
2. Generate API key in dashboard
3. Create pricing plan (credit-based)
4. Set environment variables:

```bash
cd agents/seller-simple-agent
cp .env.example .env
# Edit .env:
NVM_API_KEY=sandbox:your-api-key
NVM_ENVIRONMENT=sandbox
NVM_PLAN_ID=your-plan-id
```

5. Restart A2A agent:

```bash
poetry run agent-a2a --port 9000
```

## 📁 Project Structure

```
seller-simple-agent/
├── src/
│   ├── web_demo.py              # WebDemo server (8080)
│   │   - FastAPI app
│   │   - Landing page HTML
│   │   - POST /api/scan endpoint
│   │   - CORS + rate limiting
│   │
│   ├── agent_a2a.py             # A2A agent server (9000)
│   │   - JSON-RPC endpoint
│   │   - Agent discovery card
│   │   - Payment validation
│   │   - Nevermined integration
│   │
│   ├── tools/
│   │   ├── compliance_check.py   # Core compliance engine
│   │   │   - FTC, FDA, SEC, privacy checks
│   │   │   - Claude-powered analysis
│   │   │   - Risk scoring
│   │   │
│   │   ├── web_search.py         # Research tool
│   │   ├── summarize.py          # Summarization
│   │   └── youtube_transcript.py  # Video analysis
│   │
│   ├── observability.py          # Logging + monitoring
│   ├── log.py                    # Log configuration
│   └── client.py                 # Test client
│
├── pyproject.toml                # Poetry dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

## 🧪 Testing

### Quick Manual Tests

```bash
# Test WebDemo API
curl -X POST http://localhost:8080/api/scan \
  -H "Content-Type: application/json" \
  -d '{"content": "Test content", "detail_level": "quick"}'

# Check A2A agent is alive
curl http://localhost:9000/.well-known/agent.json | jq .name

# Test health
curl http://localhost:8080/api/health
```

### Running Tests

```bash
# Run unit tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_compliance.py
```

## 🚢 Deployment

### Local Development

```bash
poetry run web-demo &
poetry run agent-a2a --port 9000 &
```

### Production (AWS + Strands SDK)

```bash
poetry run agent-agentcore
```

### Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
RUN pip install poetry
COPY . .
RUN poetry install
CMD ["poetry", "run", "web-demo"]
```

Build and run:
```bash
docker build -t compliance-shield .
docker run -p 8080:8080 compliance-shield
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# LLM Provider
OPENAI_API_KEY=sk-your-key              # For OpenAI models
ANTHROPIC_API_KEY=sk-ant-your-key       # For Claude models
GROQ_API_KEY=gsk-your-key               # For Groq models

# Nevermined (A2A Agent)
NVM_API_KEY=sandbox:your-api-key        # From nevermined.app
NVM_ENVIRONMENT=sandbox                 # sandbox, staging_sandbox, or live
NVM_PLAN_ID=your-plan-id                # Create in Nevermined App

# Service Configuration
DEMO_PORT=8080                          # WebDemo port
A2A_PORT=9000                           # A2A Agent port
DEBUG=true                              # Enable debug logging
LOG_LEVEL=INFO                          # Logging level (DEBUG, INFO, WARNING, ERROR)
```

### Running with Custom Config

```bash
# Custom ports
DEMO_PORT=9090 poetry run web-demo
A2A_PORT=9091 poetry run agent-a2a

# Specific LLM
ANTHROPIC_API_KEY=sk-ant-xxx poetry run web-demo

# Debug mode
DEBUG=true poetry run agent-a2a
```

## 📊 19 Features Shipped

✅ **REST API** — WebDemo scanning endpoint
✅ **A2A Agent** — Nevermined-integrated service
✅ **FTC Compliance** — Health claim checking
✅ **FDA Compliance** — Drug/supplement rules
✅ **SEC Compliance** — Investment claim rules
✅ **Privacy Checks** — GDPR/CCPA violations
✅ **Risk Scoring** — Overall risk level
✅ **Per-Claim Analysis** — Individual claim breakdown
✅ **Compliance Score** — 0-100 scale
✅ **Video Analysis** — YouTube transcript scanning
✅ **Rewrite Suggestions** — How to fix violations
✅ **Landing Page** — Product marketing site
✅ **Rate Limiting** — 30 requests/minute per IP
✅ **CORS Support** — Cross-origin requests
✅ **Payment Integration** — Nevermined x402
✅ **Credit-Based Pricing** — 1-10 credits per scan
✅ **Agent Discovery** — /.well-known/agent.json
✅ **Error Handling** — Detailed error messages
✅ **Logging** — Full audit trail

## 🎯 Hackathon Achievements

**Nevermined AI Agent Hackathon 2026**
- March 5-6, 2026 | AWS Loft, San Francisco

✅ **Completion**:
- [x] Multi-service architecture (WebDemo + A2A)
- [x] Nevermined x402 payment integration
- [x] 4 compliance scanning modes
- [x] 4 compliance categories (FTC, FDA, SEC, Privacy)
- [x] 100+ compliance scans validated
- [x] E2E tested and production-ready
- [x] Deployed to AWS with ngrok tunnel

## 📚 Related Documentation

- [Project README](../../README.md) — Overall project overview
- [Quick Start](../../docs/QUICK-START.md) — 5-minute setup
- [API Reference](../../docs/API-REFERENCE.md) — Complete API docs
- [Nevermined Docs](https://nevermined.ai/docs) — Payment integration

## 🔗 External Resources

- [Nevermined App](https://nevermined.app) — API keys & plans
- [x402 Protocol](https://github.com/coinbase/x402) — HTTP payment spec
- [FTC Guides](https://www.ftc.gov/business-guidance) — Health claims rules
- [FDA Compliance](https://www.fda.gov/drugs) — Drug/supplement rules
- [SEC Rules](https://www.sec.gov/cgi-bin) — Investment regulations

## 📝 License

MIT

---

**Ready to scan?** Start with:
```bash
poetry run web-demo
# Open http://localhost:8080
```

**Questions?** See [README.md](../../README.md) or the [API Reference](../../docs/API-REFERENCE.md).
