# ComplianceShield — Demo Day Cheat Sheet (March 6, 2026)

## Quick Start (if services died overnight)

```bash
bash ~/hackathon-compliance/restart-all.sh
ngrok http 9000   # separate terminal
```

## Service Health Check

```bash
curl -s localhost:8080 > /dev/null && echo "Web: OK" || echo "Web: DOWN"
curl -s localhost:9000 > /dev/null && echo "A2A: OK" || echo "A2A: DOWN"
curl -s localhost:3000/health > /dev/null && echo "MCP: OK" || echo "MCP: DOWN"
curl -s localhost:8000 > /dev/null && echo "Buyer: OK" || echo "Buyer: DOWN"
```

## Demo URLs (show on YOUR laptop)

| What | URL |
|------|-----|
| Product page (scan videos here) | http://localhost:8080 |
| Dashboard (live stats) | http://localhost:8080/dashboard.html |
| Buyer agent (agent economy) | http://localhost:8000 |
| Agent card (for other teams) | http://localhost:9000/.well-known/agent.json |
| API docs | http://localhost:8080/api-docs.html |

## Test Videos (paste into scanner)

| Video | URL | Expected |
|-------|-----|----------|
| Liver King (BEST) | `https://www.youtube.com/watch?v=q_Vd7i4ZpgA` | 6 issues, score 42, 3 HIGH (health+FTC). ~23s |
| Coffeezilla sponsor | `https://www.youtube.com/watch?v=mHJ3rJZv2a4` | 7 issues, score 28, 2 HIGH (FTC). ~22s |
| Coffeezilla CryptoZoo | `https://www.youtube.com/watch?v=386p68_lDHA` | Clean (investigative journalism). ~21s |

## Backup Text (if YouTube fails)

Paste this into the text scanner:
```
Hey guys! So I've been using this amazing new supplement called KetoBlast Pro and I lost 30 pounds in just 2 weeks! You HAVE to try it - it literally cures inflammation and reverses aging. My doctor was SHOCKED. Use my code HEALTH50 for 50% off at the link in my bio. Also, I've been investing in this new crypto token and it's guaranteed to 10x by next month - not financial advice lol but seriously put your savings in it.
```

## 3-Minute Pitch

**[30s] The Problem:**
"FTC fined creators $100M+ last year. One video = $50K fine. Lawyers charge $500/hr."

**[90s] Live Demo:**
1. Open localhost:8080 - "This is ComplianceShield"
2. Paste Liver King URL - wait 30s - report appears
3. Show issues: "6 violations found — 3 HIGH risk. Health claims, FTC deception, each with the specific law and a link to it"
4. Switch to text tab - paste backup text - instant scan

**[30s] Agent Economy:**
"Not just a website - it's an AI agent." Show buyer at localhost:8000
"Any agent discovers, pays, uses our tools. A2A, MCP, HTTP - 3 protocols, 1 service."

**[30s] Close:**
"50M creators need this. $29/mo. The compliance layer for the agent economy. ComplianceShield - stop getting fined, start creating safely."

## Networking Script (for other teams)

Walk up and say:
"Hey! My compliance agent is live - point your buyer at this URL and get free compliance scans:"
```
https://candelaria-fierce-ingeniously.ngrok-free.dev
```

"What does your agent sell? I want to buy from you too."

Every cross-team transaction = points for Most Interconnected ($1K).

## If Something Breaks

```bash
# Kill everything and restart
pkill -f "src.agent_a2a" ; pkill -f "src.web" ; pkill -f "web_demo" ; pkill -f "mcp_server"
sleep 2
bash ~/hackathon-compliance/restart-all.sh
```

## GitHub Repo

https://github.com/agi-developr/complianceshield

## Prizes We're Targeting

| Prize | $ | Strategy |
|-------|---|----------|
| Best Seller | $1K | We ARE a seller - 4 tools, tiered pricing, real transactions |
| Ability.ai | $2K | Automates $500/hr legal work for $1 |
| Best Global | $3K | 3 protocols, working product, real business model |
| Most Interconnected | $1K | Network with EVERY team, share ngrok URL |
