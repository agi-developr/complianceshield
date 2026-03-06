# ComplianceShield — Demo Day Backlog

## YOU MUST DO (only you can do these)

### Critical (Before Demo)
- [ ] **Add to Google Sheet Ideas Board** — https://docs.google.com/spreadsheets/d/1R-ohHM-NZbTJ9KDgiQmNro1zot2rMEf0XtcXyYzZ9yA
  - Team name: ComplianceShield
  - Agent URL: https://candelaria-fierce-ingeniously.ngrok-free.dev
  - Description: AI-powered legal compliance checker for content creators
- [ ] **Restart services** to pick up code improvements (rate limiting, error handling)
  - Run: `bash ~/hackathon-compliance/restart-all.sh`
  - Then: `ngrok http 9000` in a separate terminal
- [ ] **Practice the 3-minute pitch** — see DEMO-DAY-CHEATSHEET.md

### Networking (For "Most Interconnected" Prize)
- [ ] Share ngrok URL with EVERY team: `https://candelaria-fierce-ingeniously.ngrok-free.dev`
- [ ] Walk up and say: "My compliance agent is live. Point your buyer at this URL for free scans."
- [ ] Ask each team: "What does your agent sell? I want to buy from you too."
- [ ] Each cross-team transaction = points for Most Interconnected ($1K)

### During Demo
- [ ] Have localhost:8080 open (product page)
- [ ] Have localhost:8080/dashboard.html open (live stats)
- [ ] Have localhost:8000 open (buyer agent — agent economy story)
- [ ] Paste Liver King URL first (most impressive — 6 issues, 3 HIGH risk)
- [ ] Have backup text ready if YouTube is slow (see cheatsheet)

## ALREADY DONE (by AI)

### Code Improvements (applied, need restart)
- [x] Input validation on all scan endpoints (empty content, max length)
- [x] Rate limiting (30 req/min per IP) on all scan endpoints
- [x] Proper error responses with consistent JSON format
- [x] YouTube URL validation and max length checks
- [x] Batch scan item validation
- [x] URL scan validation

### Testing (all passed)
- [x] Text scan: 3 content types tested (health, financial, compliant) — all correct
- [x] Video scan: Liver King video — 6 issues found, score 42, 23s
- [x] Batch scan: 2 items — both processed correctly
- [x] URL scan: httpbin.org — extracted Moby Dick passage, score 100
- [x] Stats endpoint: accurate counts
- [x] History endpoint: returns last 50 scans
- [x] Health endpoint: returns OK
- [x] Badge endpoints: return valid SVGs
- [x] Webhook registration: works
- [x] Agent card: 4 skills, correct metadata
- [x] MCP health: OK
- [x] Buyer agent: responding
- [x] ngrok tunnel: live

### Frontend (already built)
- [x] Landing page with 4 scan modes (video, text, upload, URL)
- [x] Animated circular compliance score gauge
- [x] Scanning progress indicator
- [x] Dashboard with 10s auto-refresh + 30s health checks
- [x] 13 product pages total

### Bug Fixes
- [x] Connect page REST API pointed to port 3000 — fixed to 8080
- [x] Connect page REST API used wrong field name "text" — fixed to "content"

## NICE TO HAVE (Post-Hackathon SaaS)

### Product
- [ ] User authentication (Supabase Auth)
- [ ] Persistent scan history (database, not in-memory)
- [ ] PDF report export
- [ ] Chrome extension for YouTube Studio
- [ ] Stripe billing integration
- [ ] Custom domain (complianceshield.ai)

### Technical
- [ ] Database storage (Supabase/PostgreSQL) instead of in-memory
- [ ] Redis for rate limiting (currently in-memory, resets on restart)
- [ ] Proper logging to file/CloudWatch
- [ ] CI/CD pipeline
- [ ] Docker Compose for one-command deploy
- [ ] Automated testing suite

### Business
- [ ] Landing page analytics (PostHog/Plausible)
- [ ] Email collection for waitlist
- [ ] Content marketing (blog about FTC fines)
- [ ] ProductHunt launch
- [ ] Instagram/TikTok platform support
