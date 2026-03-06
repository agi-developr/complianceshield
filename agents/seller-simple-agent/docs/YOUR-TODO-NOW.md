# ComplianceShield — Hackathon Status

## ALL SERVICES RUNNING

| Service | Port | Status | URL |
|---------|------|--------|-----|
| Seller Agent (A2A) | 9000 | RUNNING | **https://candelaria-fierce-ingeniously.ngrok-free.dev** |
| Buyer Agent (Web UI) | 8000 | RUNNING | http://localhost:8000 |
| Product Demo | 8080 | RUNNING | http://localhost:8080 |
| MCP Server | 3000 | RUNNING | http://localhost:3000 |

## TRANSACTIONS COMPLETED

- Plan ordered: `0xed8557ab...` (100 credits)
- 2 paid A2A transactions executed (98 credits remaining)
- Mandatory hackathon requirement: MET

## PRODUCT PAGES

| Page | URL | What It Shows |
|------|-----|---------------|
| Landing | http://localhost:8080 | Hero + YouTube/text scanner + report renderer |
| Dashboard | http://localhost:8080/dashboard.html | Live stats from API + text/video scanners |
| Login | http://localhost:8080/login.html | Login/signup UI (redirects to dashboard) |
| Reports | http://localhost:8080/reports.html | Sample detailed compliance report |
| API Docs | http://localhost:8080/docs | Auto-generated FastAPI docs |

## DEMO VIDEOS (Paste in YouTube scanner)

| Video | URL | Expected Issues |
|-------|-----|-----------------|
| Liver King confession | `https://www.youtube.com/watch?v=q_Vd7i4ZpgA` | Health claims, supplement fraud, FTC |
| Coffeezilla CryptoZoo | `https://www.youtube.com/watch?v=386p68_lDHA` | Crypto fraud, financial claims |
| Coffeezilla worst sponsor | `https://www.youtube.com/watch?v=mHJ3rJZv2a4` | Undisclosed sponsorship |

## WHAT TO DEMO (3 min presentation)

### Slide 1: The Problem (30s)
"FTC fined influencers $100M+ last year. A single YouTube video costs $50K in fines. Lawyers charge $500/hr. We built an AI that does it in 30 seconds for $1."

### Slide 2: Live Demo (90s)
1. Open http://localhost:8080 — show landing page
2. Click "Try sample video" or paste Liver King URL
3. Wait ~30s — beautiful compliance report appears (HIGH RISK, 9 issues, specific regulations, fixes)
4. Switch to "Paste Text" tab — show text scanning
5. Open http://localhost:8080/dashboard.html — live stats updating

### Slide 3: Agent Economy (30s)
"Any AI agent can discover and pay for our compliance tools. Zero integration."
- Show ngrok URL serving agent card
- Show buyer UI (http://localhost:8000) with transaction
- "We support A2A, MCP, and HTTP — three protocols, one service"

### Slide 4: Close (30s)
"ComplianceShield. 50M creators need this. $29/mo for creators, API for agent developers. The compliance layer for the agent economy."

## NETWORKING — Share This With Other Teams

```
Our compliance agent URL:
https://candelaria-fierce-ingeniously.ngrok-free.dev

Test it:
curl https://candelaria-fierce-ingeniously.ngrok-free.dev/.well-known/agent.json \
  -H "ngrok-skip-browser-warning: true"
```

## IF SOMETHING CRASHES

```bash
# Seller agent:
cd ~/hackathon-compliance/agents/seller-simple-agent
poetry run python -m src.agent_a2a --port 9000 --buyer-url http://localhost:8000

# Buyer agent:
cd ~/hackathon-compliance/agents/buyer-simple-agent
poetry run python -m src.web

# Web demo:
cd ~/hackathon-compliance/agents/seller-simple-agent
poetry run python -c "from src.web_demo import main; main()"

# MCP server:
cd ~/hackathon-compliance/agents/seller-simple-agent
poetry run python -c "from src.mcp_server import main; main()"

# ngrok:
ngrok http 9000
```

## PRIZE STRATEGY

| Prize | $ | Our Chance | Why |
|-------|---|-----------|-----|
| Best Seller | $1K | HIGH | We ARE a seller with tiered pricing |
| Ability.ai | $2K | HIGH | Real business automation, no API lock-in |
| Best Global | $3K | MEDIUM | Strong demo + real transactions |
| Mindra | $2K | MEDIUM | Only if we integrate their platform |
| Most Interconnected | $1K | MEDIUM | Depends on cross-team transactions |
