# ComplianceShield — Hackathon Demo Script (3 min)

## Opening (30s)

"Last year, the FTC fined influencers over $100 million for undisclosed sponsorships and false health claims. A single YouTube video can cost you $50,000 in fines. Lawyers charge $500 an hour to review your content. We built something better."

## Live Demo (90s)

### Step 1: Show the Product (15s)
- Open ComplianceShield landing page (http://localhost:8080)
- "This is ComplianceShield. Drop a YouTube URL, get a legal compliance report."

### Step 2: Scan a Real Video (45s)
- Paste a YouTube URL with compliance issues into the scanner
- "Watch — we extract the transcript, run it through our AI legal analyzer, and..."
- Report appears with HIGH RISK warning, specific issues flagged
- "Three FTC violations, two health claims, one financial advice issue. Each with the specific regulation it violates and how to fix it."

### Step 3: Show the Agent Economy (30s)
- Switch to buyer agent UI (http://localhost:8000)
- "But here's where it gets interesting. ComplianceShield isn't just a website. It's an AI agent in the Nevermined economy."
- Show the seller card: "Any agent can discover us, pay us, and use our compliance tools. Zero integration needed."
- Show cross-team transactions: "We've already processed X transactions from Y different teams today."

## The Architecture (30s)

"Three protocols, one service:
- **HTTP** for the product website — creators scan their videos
- **A2A** for the agent economy — any AI agent pays and uses our service
- **MCP** for developer tools — plug into Claude Desktop, OpenClaw, Cursor

Every transaction flows through Nevermined's payment protocol. Credits in, compliance reports out."

## The Business (30s)

"Creator economy: 50 million creators. Average FTC fine: $50,000. Our price: $29/month. We're not replacing lawyers — we're the smoke detector that tells you to call one.

Post-hackathon: freemium for creators, API for agencies, white-label for platforms. The compliance layer for the entire creator economy."

## Close (15s)

"ComplianceShield. Stop getting fined. Start creating safely. And in the agent economy — we're the compliance infrastructure everyone needs."

---

## Backup Demo Content

If YouTube extraction fails, use this pre-written content:

```
Hey guys! So I've been using this amazing new supplement called KetoBlast Pro and I lost 30 pounds in just 2 weeks! You HAVE to try it — it literally cures inflammation and reverses aging. My doctor was SHOCKED. Use my code HEALTH50 for 50% off at the link in my bio. Also, I've been investing in this new crypto token and it's guaranteed to 10x by next month — not financial advice lol but seriously put your savings in it. Oh and did you guys see what happened with [celebrity name]? I heard from a source that they're getting divorced because of [private details]...
```

This content triggers: FTC (undisclosed sponsorship), Health (unsubstantiated claims), Financial (investment guarantees), Privacy (celebrity gossip).

## Technical Quick Reference

```bash
# Terminal 1: Seller (A2A + compliance tools)
cd seller-simple-agent && poetry run python -m src.agent_a2a --port 9000

# Terminal 2: Buyer (web UI)
cd buyer-simple-agent && poetry run python -m src.web

# Terminal 3: Product landing page
cd seller-simple-agent && poetry run python -m src.web_demo

# Terminal 4: MCP server
cd seller-simple-agent && poetry run python -m src.mcp_server

# Terminal 5: ngrok tunnels
ngrok http 9000  # seller A2A (share with other teams)
ngrok http 8080  # product demo page
```
