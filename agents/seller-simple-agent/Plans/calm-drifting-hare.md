# Submission Readiness — Final Checklist

## Context

Hackathon presentation/submission is NOW. All services are built and verified working. This plan covers what's confirmed working, what judges will see, and any last-minute actions.

## System Status: ALL GREEN (verified just now)

| Service | Port | Status | What It Does |
|---------|------|--------|--------------|
| WebDemo | 8080 | 200 OK | Landing page, scanner, dashboard, 13 pages |
| A2A Agent | 9000 | 200 OK | Payment-gated compliance (JSON-RPC + Nevermined x402) |
| MCP Server | 3000 | 200 OK | Claude Desktop tool integration |
| Buyer Agent | 8000 | 200 OK | Web UI for discovering/purchasing from sellers |

**Scanner API**: Working — returns structured compliance reports with regulation citations, risk levels, recommended fixes
**Agent Card**: 4 skills (Quick Scan, Full Analysis, Deep Review, YouTube Scan), Nevermined plan ID present
**All 8 critical pages**: 200 OK (index, dashboard, payments, connect, api-docs, pricing, login, agent.json)

## Submission Files Already Ready

| File | Status | Contents |
|------|--------|----------|
| `SUBMISSION.md` | DONE | Full writeup: problem ($337M FTC), solution, architecture diagram, 40+ features, business model, market sizing |
| `DEMO-SCRIPT.md` | DONE | 3-minute presentation: hook → live demo → agent economy → architecture → business → close |
| `docs/YOUR-TODO-NOW.md` | DONE | Status tracker with transaction history |

### Two-Agent Setup (No Code Changes Needed for Buyer)

**Agent 1: Compliance Checker SELLER** (your custom build)
- Port 9000 (A2A mode): `poetry run python -m src.agent_a2a --port 9000 --buyer-url http://localhost:8000`
- 3 tools: quick_scan (1cr), full_analysis (5cr), deep_review (10cr)
- Auto-registers with your buyer AND other teams' buyers

**Agent 2: Buyer Agent** (starter kit, no changes)
- Port 8000: `poetry run python -m src.web`
- Web UI at http://localhost:8000 — shows sellers, chat, activity log
- Auto-discovers other teams' sellers
- Has budget management built in

### The Networking Play (50% of Winning)

**Hour 1-2 at hackathon**: Get both agents running, verify payment flow works between them

**Hour 3+**: Walk to EVERY team and do TWO things:
1. "My compliance agent is running at [ngrok URL]. Point your buyer at it — free compliance checks!" → Gets you SELLER transactions
2. "What does your agent sell? I want to buy from you." → Gets you BUYER transactions
3. Give them the command: `--buyer-url http://[your-ngrok]/api/agent` to auto-register your seller with their buyer

**This is how you win "Most Interconnected"** — be the most social person in the room.

## Day 1 Timeline (Thursday) — Get Transaction by 4PM

| Time | Action | Notes |
|------|--------|-------|
| 9:30 | Arrive, register, get 20 USDC | Bring physical ID |
| 9:45 | Set up laptop, clone if needed | Should already be cloned |
| 10:00 | Start seller agent (A2A mode) | `poetry run python -m src.agent_a2a` |
| 10:15 | Start buyer agent (web mode) | `poetry run python -m src.web` |
| 10:30 | Test buyer→seller payment locally | Open http://localhost:8000, buy from your own seller |
| 11:00 | Set up ngrok for public URL | `ngrok http 9000` (seller) and `ngrok http 8000` (buyer) |
| 11:30 | **NETWORKING SPRINT #1** | Walk to 3-5 teams, pitch compliance API, get their agent URLs |
| 12:00 | Lunch + register with other teams' buyers | Point your seller at their buyer URLs |
| 1:00 | Execute cross-team transactions | Buy from 2+ other teams using your buyer |
| 2:00 | **First cross-team transaction MUST be done** | |
| 3:00 | **NETWORKING SPRINT #2** | Hit remaining teams you missed |
| 4:00 | Have 3+ cross-team transactions | Both buying and selling |
| 5:00 | Add any Day 2 improvements | |
| 6:00 | Mandatory deadline: first paid transaction | Should be done hours ago |

## Day 2 Timeline (Friday) — Polish and Present

| Time | Action |
|------|--------|
| 9:30 | Check overnight — any new sellers registered with your buyer? |
| 10:00 | **NETWORKING SPRINT #3** — final push for transactions |
| 11:00 | Maximize transaction count: buy from every available team |
| 12:00 | Prepare demo (see script below) |
| 1:00 | Practice demo twice |
| 2:00 | Final transaction push |
| 3:00+ | Presentations |

## Demo Script (3 Minutes)

### Slide 1: The Problem (30s)
"Content creators face $50K+ FTC fines. Lawyers cost $500/hour. But in the agent economy, compliance checking should be as easy as an API call."

### Slide 2: Live Demo (90s)
1. Open buyer web UI — show sellers registered in sidebar
2. Paste problematic nutrition advice transcript in chat
3. "Purchase compliance scan from Compliance Checker"
4. Watch real-time compliance report stream in
5. Show the payment settled — credits deducted
6. "Any agent in this room can do what I just did. No integration needed — just point at our A2A endpoint."

### Slide 3: The Numbers (30s)
"We processed X transactions from Y different teams. Our buyer also purchased Z services. Total cross-team value: N credits."
Show the `/stats` endpoint and buyer activity log.

### Slide 4: The Vision (30s)
"Every content agent needs a compliance layer. We're that layer. Post-hackathon: $29/mo for creators, API for agent developers. The compliance agent that scales with the agent economy."

## Prize Targeting

| Prize | $ | How to Win It |
|-------|---|---------------|
| **Most Interconnected** | $1K | Most cross-team transactions (buy + sell). BE SOCIAL. |
| **Best Seller** | $1K | 2+ teams buying compliance checks, 3+ transactions |
| **Best Global** | $3K | Strong demo + real transactions + compelling narrative |
| **ZeroClick** ($2K) | $2K | "Compliance enables safe content monetization" — content creators need this before ZeroClick ads work |
| **Ability.ai** ($2K) | $2K | "We automated what compliance lawyers do — any business agent can use our service" |
| **Mindra** ($2K) | $2K | "Our agent plugs into any orchestration pipeline — Mindra workflows can add compliance checking in one step" |

## Technical Checklist for Hackathon Day

### Before You Leave Home
- [ ] Laptop charged, charger packed
- [ ] Physical ID (digital not accepted)
- [ ] `.env` files configured for both seller and buyer agents
- [ ] `poetry install` done for both agents
- [ ] Frontend built: `cd buyer-simple-agent/frontend && npm install && npm run build`
- [ ] ngrok installed: `brew install ngrok` (or download)
- [ ] Test: seller starts, buyer starts, buyer→seller payment works locally

### At the Venue
- [ ] Connect to WiFi: Guest network, password "BrokenWires@@2019"
- [ ] Start seller: `cd seller-simple-agent && poetry run python -m src.agent_a2a --port 9000`
- [ ] Start buyer: `cd buyer-simple-agent && poetry run python -m src.web`
- [ ] Expose seller via ngrok: `ngrok http 9000`
- [ ] Expose buyer via ngrok: `ngrok http 8000`
- [ ] Share your seller ngrok URL with other teams
- [ ] Register other teams' sellers with your buyer

### Critical Commands Reference

```bash
# Start compliance checker (seller, A2A mode)
cd ~/hackathon-compliance/agents/seller-simple-agent
poetry run python -m src.agent_a2a --port 9000 --buyer-url http://localhost:8000

# Start buyer (web UI mode)
cd ~/hackathon-compliance/agents/buyer-simple-agent
poetry run python -m src.web

# Expose to other teams
ngrok http 9000  # seller → share this URL
ngrok http 8000  # buyer → for others to register with you

# Other teams connect to you:
# They run their seller with: --buyer-url https://YOUR-NGROK.ngrok-free.app/api/agent
# You connect to their seller by asking your buyer: "discover agent at https://THEIR-URL"
```

## Remaining Setup Work

1. **Buyer agent `.env`** — Copy `.env.example`, add NVM credentials (same API key works)
2. **Buyer agent `poetry install`** — Install dependencies
3. **Buyer frontend build** — `cd frontend && npm install && npm run build`
4. **ngrok setup** — `brew install ngrok` + authenticate
5. **Bedrock form** — Check if approved; if not, Anthropic API works fine
6. **Strands agent model** — Need either OpenAI key or Bedrock for the routing agent brain. Can use Anthropic via Bedrock once approved, or get an OpenAI key as backup ($5 minimum)

## Verification

- [ ] Seller starts and registers on Nevermined
- [ ] Buyer starts and shows web UI
- [ ] Seller auto-registers with buyer (appears in sidebar)
- [ ] Buyer can purchase compliance check from seller
- [ ] Payment settles correctly (credits deducted)
- [ ] Stats endpoint shows transaction count
- [ ] ngrok URLs are accessible from another device
