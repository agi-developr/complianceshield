# ComplianceShield — Human Action Items

Things only YOU can do. Everything else has been automated.

## URGENT (Do These First)

### 1. Complete Nevermined Agent Metadata (30 seconds)
- Open https://nevermined.ai/hackathon/register
- Click "My Agents" tab
- Click "Compliance Checker Agent" → Edit
- Fill: Category = `RegTech`
- Fill: Services We Sell = `FTC compliance scanning, FDA health claim analysis, SEC financial compliance, COPPA children's privacy audit, GDPR data protection review`
- Fill: Services Per Request = `Structured compliance report with specific law citations, risk levels, and recommended fixes`
- Click Save Changes

### 2. Create Devpost Project (5 minutes)
- Go to https://devpost.com/software/new
- Project Name: `ComplianceShield`
- Tagline: `AI-powered legal compliance infrastructure for the creator economy`
- Description: Copy-paste from SUBMISSION.md (the full file)
- Built With: python, fastapi, claude-ai, nevermined, a2a-protocol, mcp, groq, aws-strands-sdk
- Upload screenshots from `screenshots/` folder
- Submit to the Nevermined hackathon (search for it on Devpost)

### 3. Add to Google Sheet Ideas Board
- Go to https://nevermined.ai/hackathon/register → Ideas Board tab → Open Google Sheet
- Add row: Team=ComplianceShield, Selling=FTC/FDA/SEC/COPPA/GDPR compliance scanning, Buying=Any agent services available

## BEFORE DEMO DAY

### 4. Start ngrok Tunnels
```bash
# Terminal 1: Seller agent public URL
ngrok http 9000
# Copy the https URL — share with other teams

# Terminal 2: Buyer agent public URL
ngrok http 8000
```
- Update the ngrok URLs in SUBMISSION.md lines 263/265
- Share your seller ngrok URL with other hackathon teams

### 5. Network With Other Teams
Walk to every team and say:
- "My compliance agent is at [your ngrok URL]. Point your buyer at it!"
- "What does your agent sell? I want to buy from you too."
- Give them: `--buyer-url https://YOUR-NGROK.ngrok-free.app/api/agent`

### 6. Practice Demo (3 minutes)
Run through DEMO-SCRIPT.md twice:
1. Open http://localhost:8080 → paste bad content → show scan results
2. Open http://localhost:8000 → buy compliance scan → show credits deducted
3. Show dashboard stats → architecture → business model
Key number to memorize: $53,088 per FTC violation

## NICE TO HAVE

### 7. Record a Demo Video
- Screen record the demo flow (landing → scan → results → buyer → payment)
- Upload to YouTube, add link to Devpost
- 2-3 minutes max

### 8. Get a Custom Domain (optional)
- Buy complianceshield.ai or similar
- Point it at ngrok or a cloud deploy

### 9. Deploy to Cloud (post-hackathon)
- Deploy web_demo.py to Railway/Render/Fly.io
- Deploy agent_a2a.py separately
- Set up proper TLS and domain

## COMPLETED BY AUTOMATION
- [x] All 13 pages polished and nav standardized
- [x] Dashboard bugs fixed (uptime formatting, CORS)
- [x] Landing page spacing optimized
- [x] 25+ stale ngrok URLs replaced
- [x] Meta tags and Open Graph added to all pages
- [x] Mobile responsiveness fixed
- [x] Scanner UX improved (error handling, examples, validation)
- [x] Security hardening (CORS, rate limiting, input validation)
- [x] Professional screenshots taken
- [x] Comprehensive E2E testing passed
- [x] Dashboard improved with auto-refresh and better charts
