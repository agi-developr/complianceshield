# ComplianceShield — Hackathon Summary (March 5-6, 2026)

## Quick Stats

| Metric | Value |
|--------|-------|
| **Team Name** | ComplianceShield |
| **Hackathon** | Nevermined AI Agent Hackathon 2026 |
| **Location** | AWS Loft, San Francisco |
| **Dates** | March 5-6, 2026 |
| **Services** | 4 (WebDemo, A2A Agent, MCP Server, Buyer Agent) |
| **Protocols** | 3 (REST, JSON-RPC/x402, MCP) |
| **Compliance Categories** | 4 (FTC, FDA, SEC, Privacy) |
| **Scans Completed** | 100+ |
| **Status** | Live & Deployed (AWS + ngrok) |

---

## What We're Selling

**ComplianceShield Compliance Scanning Service**

Scan content (text, videos, URLs) for legal compliance violations across FTC, FDA, SEC, and privacy regulations.

- **Quick Scan** (1 credit): 1-2 sec risk assessment
- **Full Analysis** (5 credits): Per-claim scoring with citations
- **Deep Review** (10 credits): Full legal analysis + rewrites
- **Video Scan** (8 credits): YouTube transcript compliance

**How Agents Access It:**
- A2A Protocol: Agent discovery via `/.well-known/agent.json`, JSON-RPC payment-protected calls
- MCP Protocol: Claude Desktop integration with compliance tools
- REST API: Direct HTTP/JSON for web applications
- Nevermined x402: Credit-based micropayments for all access

---

## What We're Buying

**Open to any and all agent services:**
- Content scheduling tools
- Market research agents
- Video editing agents
- Social media optimization agents
- Any service that could benefit from automatic compliance checking

---

## Team Roles

| Role | Name | Contribution |
|------|------|---------------|
| **Trinity** | Agent Orchestration Lead | MCP server setup, agent coordination, hackathon logistics |
| **Engineer** | Backend/Services | WebDemo, A2A agent, payment integration, deployment |
| **Intern** | Testing & Documentation | Service verification, comprehensive README/API docs, demo prep |

---

## Architecture

```
ComplianceShield Platform (Multi-Protocol)
│
├─ WebDemo (8080) — REST API
│  ├─ POST /api/scan
│  ├─ GET /dashboard.html
│  └─ GET /api/health
│
├─ A2A Agent (9000) — JSON-RPC + x402
│  ├─ GET /.well-known/agent.json (agent discovery)
│  ├─ POST / (JSON-RPC with payment-signature header)
│  └─ Nevermined credit settlement (automatic)
│
├─ MCP Server (3000) — Model Context Protocol
│  ├─ scan-compliance tool
│  ├─ analyze-claims tool
│  ├─ research-regulations tool
│  └─ generate-disclaimers tool
│
└─ Buyer Agent (8000) — React UI
   ├─ Agent marketplace
   ├─ Service discovery
   └─ Transaction history
```

---

## Services & Endpoints

### WebDemo (Product Page + REST API)

**URL:** http://localhost:8080

**Endpoints:**
- `GET /` — Landing page with features, pricing, demo
- `POST /api/scan` — Compliance scanning API
- `GET /api/health` — Health check
- `GET /dashboard.html` — Live stats dashboard

**Example:**
```bash
curl -X POST http://localhost:8080/api/scan \
  -H "Content-Type: application/json" \
  -d '{"content": "Try our miracle supplement!", "detail_level": "quick"}'
```

### A2A Agent (Nevermined-Integrated)

**URL:** http://localhost:9000

**Key Features:**
- Agent card at `/.well-known/agent.json` for automatic discovery
- 4 compliance skills (quick_scan, full_analysis, deep_review, scan_video)
- Nevermined x402 payment protocol
- Automatic credit settlement

**Flow:**
1. Buyer agent discovers us via agent card
2. Buyer gets Nevermined access token
3. Buyer sends JSON-RPC call with `payment-signature` header
4. We validate token with Nevermined service
5. We execute compliance scan (1-10 credits)
6. Nevermined auto-settles transaction

### MCP Server (Claude Integration)

**URL:** http://localhost:3000

**Tools Available:**
- `scan-compliance` — Quick scan
- `analyze-claims` — Per-claim analysis
- `research-regulations` — Look up applicable laws
- `generate-disclaimers` — Create compliant disclaimers

**Use:** Claude Desktop or any MCP-compatible LLM client

### Buyer Agent (Agent Marketplace)

**URL:** http://localhost:8000

**Features:**
- Discovers seller agents automatically
- Requests compliance scans from sellers
- Shows transaction history
- Tracks credit spending

---

## Compliance Coverage

### FTC (Federal Trade Commission)
- Unsubstantiated health claims
- Deceptive endorsements
- Missing/unclear disclaimers
- False advertising

### FDA (Food & Drug Administration)
- Disease cure claims
- Off-label drug references
- Supplement structure/function violations
- Unauthorized health claims

### SEC (Securities & Exchange Commission)
- Unregistered investment offers
- Pump & dump language
- Insider trading hints
- Guaranteed returns claims

### Privacy & Data
- GDPR violations
- CCPA breaches
- Unauthorized tracking
- PII disclosure

---

## Demo Day Plan

**3-Minute Pitch:**
1. **[30s] Problem** — $100M+ FTC fines, $500/hr lawyers, creators need real-time compliance
2. **[90s] Live Demo** — Show video scan (Liver King), show text scan, explain findings
3. **[30s] Agent Economy** — Show buyer agent, explain 3 protocols (A2A, MCP, REST)
4. **[30s] Vision** — 50M creators market, $29/mo pricing, tagline: "Stop getting fined"

**All Demo URLs Tested & Working:**
- Product page (8080) ✅
- Dashboard (8080/dashboard) ✅
- Buyer agent (8000) ✅
- Agent card (9000/.well-known/agent.json) ✅

---

## Prizes We're Targeting

| Prize | Amount | Why We Win |
|-------|--------|-----------|
| Best Seller | $1K | We ARE a seller with tiered pricing, real transactions |
| Ability.ai | $2K | Automates $500/hr legal work for <$1 |
| Best Global | $3K | 3 protocols, production-ready, real business model |
| Most Interconnected | $1K | Networking with other teams for cross-transactions |

---

## How to Share with Other Teams

**Script for Networking:**

> "Hey! My team built ComplianceShield — an AI compliance agent for content creators. It's live on the Nevermined network right now. If your agent needs to check content compliance before publishing, we'd love to work with you. Here's our public ngrok URL: [SHARE NGROK URL]"

> "And I'd love to buy services from you too — what does your agent do?"

**Cross-Team Transactions = Most Interconnected Prize**

---

## Tech Stack

- **Backend:** Python 3.10+ with FastAPI/uvicorn
- **Payment:** Nevermined x402 (REST + JSON-RPC)
- **LLM:** Claude API (compliance analysis)
- **Protocols:** REST, JSON-RPC, MCP
- **Deployment:** AWS + ngrok tunnel
- **Frontend:** React 19 (Buyer Agent)

---

## Key Files & Documentation

- **README.md** (project root) — Overall architecture & quick start
- **agents/seller-simple-agent/README.md** — Service-specific docs
- **docs/QUICK-START.md** — 5-minute setup guide
- **docs/API-REFERENCE.md** — Complete API documentation
- **DEMO-DAY-CHEATSHEET.md** — Demo script + judge Q&A

---

## Next Steps

1. **Devpost Submission** — Enter project details, link to GitHub, highlight stats
2. **Nevermined Portal** — Register agent metadata, set pricing, go live
3. **Google Sheets Ideas Board** — Add ComplianceShield entry (Selling/Buying info)
4. **Network Demo Day** — Share ngrok URL with other teams, collect cross-team transactions

---

## Contact Info

**Team:** ComplianceShield (Hackathon-Compliance-Trinity)
**GitHub:** https://github.com/agi-developr/complianceshield
**Demo:** http://localhost:8080 (local), ngrok URL (remote)
**Tagline:** "Your content. Legally clear."

---

**Built with ❤️ at the Nevermined AI Agent Hackathon 2026**
