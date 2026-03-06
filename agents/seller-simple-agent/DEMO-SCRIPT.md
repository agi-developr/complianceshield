# ComplianceShield -- 3-Minute Demo Script

**Presenter notes**: Practice this twice before going on stage. Keep energy high. Do not read from the screen. Every click should already be loaded in a browser tab.

---

## Pre-Demo Setup (Do This Before You Present)

Open these tabs in order:

1. **Tab 1**: http://localhost:8080 (Product landing page)
2. **Tab 2**: http://localhost:8080/dashboard.html (Dashboard -- run 2-3 scans first so stats are populated)
3. **Tab 3**: Buyer agent UI at http://localhost:8000 (if available) or ngrok agent card URL
4. **Tab 4**: Terminal with the 4 servers running (A2A, MCP, web demo, ngrok)

Have this YouTube URL ready to paste (pick one with health/finance claims):
```
https://www.youtube.com/watch?v=<your-chosen-video>
```

Have this backup text in clipboard (if YouTube fails):
```
Hey guys! So I've been using this amazing supplement called KetoBlast Pro and I lost 30 pounds in just 2 weeks! It literally cures inflammation and reverses aging. Use my code HEALTH50 for 50% off at the link in my bio. I've also been investing in this new crypto token -- guaranteed to 10x by next month. Not financial advice lol but seriously put your savings in it.
```

---

## The Script

### [0:00 - 0:30] THE HOOK -- Why This Matters

> *Stand up. No slides. Look at the audience.*

**SAY:**

"Last year the FTC fined content creators over 100 million dollars. One YouTube video with an undisclosed sponsorship -- that is a $50,000 fine. A health supplement claim without evidence -- another $50,000. Lawyers charge $500 an hour to review your scripts, and they still miss things.

There are 200 million content creators in the world. None of them have a compliance team. We built one that costs $29 a month."

> *Turn to your screen. Tab 1 should be showing.*

---

### [0:30 - 1:15] LIVE DEMO -- Scan Real Content

> *You are on Tab 1: the product landing page.*

**SAY:**

"This is ComplianceShield. You paste content -- a YouTube URL, a script, a transcript -- and you get a legal compliance report in seconds."

**DO:** Paste the YouTube URL (or backup text) into the scanner. Click scan. Select "Full Analysis."

> *While it processes (~5 seconds):*

**SAY:**

"Under the hood we are pulling the video transcript, running it through Claude, and checking it against 25 federal regulations -- FTC Act, FDA labeling rules, SEC anti-fraud, COPPA, CAN-SPAM, HIPAA, CCPA. Every single citation links to the actual law on eCFR or law.cornell.edu."

**DO:** Report appears. Scroll through it slowly.

**SAY:**

"Three issues found. This one -- *point at the HIGH risk item* -- undisclosed sponsorship, violates 16 CFR Part 255, the FTC Endorsement Guides. Click this link -- *click the regulation URL* -- that is the actual federal regulation. Not a hallucination. The real law.

This one -- *point at the health claim* -- unsubstantiated health claim under the Federal Food, Drug, and Cosmetic Act. And the recommended fix tells you exactly how to rewrite it."

> *Do not linger. Move to the next section.*

---

### [1:15 - 1:55] THE AGENT ECONOMY -- A2A + Payments

> *Switch to Tab 3 (buyer agent or ngrok agent card).*

**SAY:**

"But ComplianceShield is not just a website. It is infrastructure for the agent economy."

**DO:** Show the agent card JSON (/.well-known/agent.json) or the buyer agent discovering ComplianceShield.

**SAY:**

"This is our A2A agent card -- standard discovery protocol. Any AI agent on the internet can find us, see our pricing, and purchase a compliance scan. No API key signup. No OAuth. Just Nevermined x402 payment tokens.

We have already completed two paid transactions from other agents on the hackathon network. Real credits. Real settlement."

**DO:** If buyer UI is available, show a completed transaction. Otherwise, show the terminal logs showing payment verification and credit settlement.

**SAY:**

"And for developers -- we also run an MCP server. Connect from Claude Desktop or Cursor, and compliance scanning is just another tool in your AI assistant. Four tools, credit-based pricing, zero integration effort."

---

### [1:55 - 2:30] THE ARCHITECTURE -- Three Protocols

> *Switch to Tab 2: Dashboard. Stats should show 5+ scans, issues found, risk scores.*

**SAY:**

"Three protocols, one compliance engine.

HTTP REST API for the product -- creators scan their own content.

A2A for the agent economy -- any AI agent discovers us, pays with x402, gets a compliance report.

MCP for developer tools -- plug ComplianceShield into Claude Desktop or Cursor as a native tool.

Every protocol hits the same compliance engine. Claude Haiku for analysis. Groq Whisper for audio transcription. Twenty-five regulation URLs mapped to official government sources."

**DO:** Point at the dashboard stats. Show total scans, issues found, average risk score.

---

### [2:30 - 2:50] THE BUSINESS -- Why This Wins

**SAY:**

"Two hundred million content creators. Average FTC fine: $50,000. Our price: $29 a month. Gross margin over 95 percent -- each scan costs us two cents in API calls.

We are not replacing lawyers. We are the smoke detector that tells you when to call one.

Post-hackathon plan: Chrome extension for YouTube Studio, API for talent agencies, white-label for platforms. The compliance layer for the entire creator economy."

---

### [2:50 - 3:00] THE CLOSE

> *Look directly at the judges.*

**SAY:**

"ComplianceShield. Three protocols. One compliance engine. Zero FTC fines.

Stop getting fined. Start creating safely."

> *Pause. Done.*

---

## If Things Go Wrong

| Problem | Recovery |
|---------|----------|
| YouTube transcript fails | Paste the backup text from clipboard. Say "Let me show you with a script instead." |
| Scan takes too long | Switch to dashboard (Tab 2), show previous scan results. Say "Here is one we ran earlier." |
| A2A server is down | Show the agent card JSON from a saved screenshot. Show terminal logs of past transactions. |
| ngrok tunnel dies | Use localhost URLs. Say "In production this runs on a public endpoint -- let me show you the local version." |
| LLM returns error | Show a cached HTML report file. Say "We generate professional HTML reports -- here is one from this morning." |

---

## Timing Cheat Sheet

| Time | Section | Key Action |
|------|---------|------------|
| 0:00 | Hook | "$50K fines. $500/hr lawyers. 200M creators." |
| 0:30 | Live Demo | Paste URL, click scan, show report |
| 1:15 | Agent Economy | Show agent card, A2A transactions, MCP |
| 1:55 | Architecture | Dashboard stats, three protocols diagram |
| 2:30 | Business | $29/mo, 95% margin, 200M TAM |
| 2:50 | Close | "Three protocols. Zero fines." |

---

## Key Numbers to Memorize

- **$53,088** -- FTC fine per violation (2025 rate)
- **$337.3M** -- FTC returns to consumers from violations (2024)
- **200M+** -- Global content creators
- **$29/month** -- Our price
- **$0.02-0.05** -- Our cost per scan
- **95%+** -- Gross margin
- **25+** -- Regulation URLs mapped
- **2** -- Paid A2A transactions completed
- **3** -- Protocols (A2A, MCP, REST)
- **4** -- Compliance tools (quick, full, video, deep)
