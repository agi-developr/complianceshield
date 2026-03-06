# ComplianceShield: AI-Powered Legal Compliance for Content Creators

**Your content. Legally clear.** — AI-powered FTC, FDA, SEC compliance scanning for content creators using Nevermined x402 payment integration.

ComplianceShield is a multi-service platform that analyzes marketing copy, social media posts, video scripts, health claims, and financial statements for compliance violations. Built during the Nevermined AI Agent Hackathon (March 5-6, 2026).

## 🚀 Quick Start

### One-Command Startup

```bash
cd /Users/ilaprihodko/hackathon-compliance
./restart-all.sh
```

This starts all 4 services:
- **WebDemo** (port 8080): Interactive web UI
- **A2A Agent** (port 9000): Agent-to-agent compliance service
- **MCP Server** (port 3000): Tool-based compliance API
- **Buyer Agent** (port 8000): Agent marketplace dashboard

### Manual Setup

```bash
# Prerequisites
python3 --version  # 3.10+
poetry --version   # Required for Python dependencies

# Install each service
cd agents/seller-simple-agent && poetry install
cd ../buyer-simple-agent && poetry install
cd ../mcp-server-agent && poetry install

# Start services (in separate terminals)
cd agents/seller-simple-agent
poetry run python -m src.web                # WebDemo (8080)
poetry run python -m src.agent_a2a --port 9000  # A2A Agent

cd agents/buyer-simple-agent
poetry run python -m src.web --port 8000   # Buyer Agent (8000)

cd agents/mcp-server-agent
poetry run python -m src.server --port 3000  # MCP Server
```

## 📋 Services Overview

### 1. WebDemo (Port 8080)
**Interactive web interface** for compliance scanning.

- **Landing page**: Features, pricing, demo
- **Dashboard**: Scan history, compliance reports
- **API**: `POST /api/scan` — Run compliance analysis

```bash
# Quick scan
curl -X POST http://localhost:8080/api/scan \
  -H "Content-Type: application/json" \
  -d '{"content": "Amazing skin cream - removes wrinkles overnight!"}'

# Response includes:
# - Overall risk level (LOW, MEDIUM, HIGH)
# - Specific violations (FTC, FDA, privacy, etc.)
# - Compliance score (0-100)
# - Rewrite suggestions
```

**Features**:
- Real-time compliance scanning
- 4 scan modes: Quick, Full, Deep, Video Analysis
- Per-claim risk assessment
- Actionable recommendations

### 2. A2A Agent (Port 9000)
**Agent-to-Agent compliance service** with Nevermined x402 payment integration.

- **Discovery**: `/.well-known/agent.json` — Agent metadata
- **Payment**: x402 protocol with Nevermined credits
- **Skills**:
  - `quick_scan` (1 credit): Fast compliance check
  - `full_analysis` (5 credits): Detailed risk scoring
  - `deep_review` (10 credits): Comprehensive legal review
  - `scan_video` (8 credits): Video transcript compliance

```bash
# Check agent metadata
curl http://localhost:9000/.well-known/agent.json | jq

# Make a payment-protected call (requires Nevermined API key)
curl -X POST http://localhost:9000/ \
  -H "Content-Type: application/json" \
  -H "payment-signature: YOUR_NEVERMINED_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "quick_scan",
    "params": {"content": "Your marketing copy here"},
    "id": 1
  }'
```

**Nevermined Integration**:
- Credit-based pricing (1-10 credits per scan)
- Automatic payment verification
- Real-time token validation
- Budget tracking and limits

### 3. MCP Server (Port 3000)
**Model Context Protocol** compliance tools for Claude/other LLMs.

```bash
# Health check
curl http://localhost:3000/health

# Response: {"status":"ok","service":"compliance-mcp-server","timestamp":"2026-03-06T..."}
```

**Available Tools**:
- `scan_compliance`: Quick compliance check
- `analyze_claims`: Extract and score individual claims
- `research_regulations`: Look up applicable regulations
- `generate_disclaimers`: Create compliant disclaimers

### 4. Buyer Agent (Port 8000)
**Marketplace dashboard** for discovering and testing compliance services.

- **UI**: React 19 web application
- **Discovery**: Lists available compliance agents
- **Testing**: Send test scans to agents
- **Payment Flow**: Integrate with Nevermined wallet

Open http://localhost:8000 in browser.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│  ComplianceShield Platform                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐  ┌──────────────┐              │
│  │ WebDemo      │  │ Buyer Agent  │              │
│  │ (8080)       │  │ (8000)       │              │
│  │ React UI     │  │ React UI     │              │
│  └──────┬───────┘  └──────┬───────┘              │
│         │                  │                       │
│         └──────────┬───────┘                       │
│                    │                               │
│         ┌──────────▼──────────┐                   │
│         │  Core Compliance    │                   │
│         │  Engine (Claude)    │                   │
│         │  - FTC rules        │                   │
│         │  - FDA guidelines   │                   │
│         │  - SEC regulations  │                   │
│         │  - Privacy laws     │                   │
│         └──────────┬──────────┘                   │
│                    │                               │
│  ┌─────────────────┼─────────────────┐           │
│  │                 │                 │           │
│  ▼                 ▼                 ▼           │
│ A2A Agent        MCP Server       External      │
│ (9000)           (3000)           APIs          │
│ x402 Protocol    Tools API        - Nevermined  │
│ Nevermined       For LLMs         - Payment     │
│                                   Validation    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 🔌 API Reference

### WebDemo Scanner API

**Endpoint**: `POST /api/scan`

**Request**:
```json
{
  "content": "string (required) — Text to scan for compliance issues",
  "detail_level": "string (optional) — 'quick' (default), 'full', 'deep'"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "detail_level": "quick",
  "report": {
    "overall_risk": "LOW|MEDIUM|HIGH",
    "summary": "Human-readable summary of findings",
    "issues": [
      {
        "type": "FTC|FDA|SEC|PRIVACY",
        "severity": "LOW|MEDIUM|HIGH",
        "claim": "The problematic claim",
        "rule": "Applicable regulation",
        "suggestion": "How to fix it"
      }
    ],
    "compliance_score": 95,
    "safe_sections": "What passed the scan",
    "disclaimer": "AI analysis disclaimer"
  },
  "report_id": "33d89058",
  "compliance_score": 95,
  "elapsed_seconds": 2.68,
  "readable": "Formatted text report"
}
```

### A2A Agent JSON-RPC API

**Endpoint**: `POST http://localhost:9000/`

**Requirements**:
- Header: `payment-signature: {Nevermined access token}`
- Body: Standard JSON-RPC 2.0

**Methods**:
- `quick_scan(content: str)` → risk report (1 credit)
- `full_analysis(content: str)` → detailed analysis (5 credits)
- `deep_review(content: str)` → legal recommendations (10 credits)
- `scan_video(transcript: str)` → video compliance (8 credits)

### MCP Server Tools

**Endpoint**: `http://localhost:3000/`

Tools available as MCP resources. Use with Claude Desktop or compatible LLM clients.

```
mcp://localhost:3000/tools/scan-compliance
mcp://localhost:3000/tools/analyze-claims
mcp://localhost:3000/tools/research-regulations
mcp://localhost:3000/tools/generate-disclaimers
```

## 💳 Payment Integration

### Nevermined x402 Protocol

All services use Nevermined's x402 protocol for payment protection:

1. **Setup**:
   - Create Nevermined API key at https://nevermined.app
   - Create pricing plan (credit-based)
   - Set `NVM_API_KEY` and `NVM_PLAN_ID` in `.env`

2. **Payment Flow**:
   - Client obtains access token from Nevermined
   - Sends `payment-signature: {token}` header
   - Service validates token and credits
   - Deducts appropriate credits on success

3. **Pricing**:
   - Quick Scan: 1 credit
   - Full Analysis: 5 credits
   - Deep Review: 10 credits
   - Video Scan: 8 credits

## 🎯 Hackathon Achievements

**Nevermined AI Agent Hackathon 2026**
- March 5-6, 2026 | AWS Loft, San Francisco

✅ **Completion Status**:
- [x] Multi-service architecture (4 services, 3 protocols)
- [x] Payment integration (Nevermined x402)
- [x] Compliance engine (FTC, FDA, SEC, privacy)
- [x] Interactive demo (WebDemo + Buyer Agent)
- [x] Agent discovery and registration
- [x] 100+ compliance scans validated
- [x] E2E testing across all services
- [x] Production-ready deployment

**Services**:
1. **WebDemo** — Interactive web UI with real-time scanning
2. **A2A Agent** — Nevermined-integrated agent service
3. **MCP Server** — Tool-based API for Claude integration
4. **Buyer Agent** — Marketplace dashboard

## 🧪 Testing

### E2E Service Verification

```bash
# All services health check
./restart-all.sh

# Test each service
curl http://localhost:8080/api/scan -X POST \
  -H "Content-Type: application/json" \
  -d '{"content": "Test"}'

curl http://localhost:9000/.well-known/agent.json
curl http://localhost:3000/health
curl http://localhost:8000
```

### Running Full Test Suite

```bash
cd agents/seller-simple-agent
poetry run pytest  # Unit + integration tests

cd ../mcp-server-agent
poetry run pytest

cd ../buyer-simple-agent
poetry run pytest
```

## 📚 Project Structure

```
hackathon-compliance/
├── agents/
│   ├── seller-simple-agent/      # WebDemo + A2A Agent
│   │   ├── src/
│   │   │   ├── agent_a2a.py      # A2A server (9000)
│   │   │   ├── web.py            # WebDemo Flask app (8080)
│   │   │   └── compliance.py      # Core compliance engine
│   │   └── pyproject.toml
│   │
│   ├── mcp-server-agent/         # MCP compliance tools
│   │   ├── src/
│   │   │   ├── server.py         # MCP server (3000)
│   │   │   └── tools/
│   │   │       ├── scan.py
│   │   │       └── research.py
│   │   └── pyproject.toml
│   │
│   └── buyer-simple-agent/       # Buyer Agent UI
│       ├── src/
│       │   ├── agent.py          # Agent logic
│       │   └── web.py            # React frontend (8000)
│       └── pyproject.toml
│
├── docs/
│   ├── getting-started.md        # Setup guide
│   ├── api-reference.md          # Full API docs
│   └── deployment.md             # Production deployment
│
├── README.md                      # This file
├── restart-all.sh               # One-command startup script
└── DEMO-DAY-CHEATSHEET.md      # Judge/demo reference
```

## 🚀 Deployment

### Local Development
```bash
./restart-all.sh
```

### Production (AWS)
```bash
# Strands SDK deployment via AgentCore
cd agents/strands-simple-agent
poetry run python agent.py --deploy
```

### Cloudflare Pages (Web Frontend)
```bash
cd agents/seller-simple-agent/web
npm run build
npm run deploy
```

## 🔐 Environment Variables

Create `.env` in each agent directory:

```bash
# Nevermined Configuration
NVM_API_KEY=sandbox:your-api-key
NVM_ENVIRONMENT=sandbox
NVM_PLAN_ID=your-plan-id

# LLM Configuration
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key

# Service Configuration
PORT=8080                    # Service port
DEBUG=true                   # Enable debug logging
LOG_LEVEL=INFO              # Logging level
```

## 📖 Documentation

- [**Getting Started**](./docs/getting-started.md) — First-time setup
- [**API Reference**](./docs/api-reference.md) — Complete endpoint documentation
- [**Compliance Rules**](./docs/compliance-rules.md) — FTC/FDA/SEC/privacy rules
- [**Deployment Guide**](./docs/deployment.md) — Production deployment
- [**Demo Script**](./DEMO-DAY-CHEATSHEET.md) — 3-minute demo walkthrough

## 🎓 Learning Resources

- [Nevermined Documentation](https://nevermined.ai/docs)
- [x402 Protocol Spec](https://github.com/coinbase/x402)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [FTC Guides for Industry](https://www.ftc.gov/business-guidance/online-advertising-promotion)
- [FDA Compliance for Claims](https://www.fda.gov/drugs/guidance-compliance-regulatory-information)

## 🤝 Team

**Hackathon Team**:
- **Trinity** (Agent Orchestration)
- **Engineer** (Backend Services)
- **Intern** (Testing & Documentation)

## 📜 License

MIT — See LICENSE file

---

**Built at Nevermined AI Agent Hackathon 2026**
*San Francisco, March 5-6*
