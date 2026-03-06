# ComplianceShield — Quick Start Guide

Get ComplianceShield running in under 5 minutes.

## Prerequisites

✅ **Python 3.10+**
```bash
python3 --version
# Python 3.10.x or higher
```

✅ **Poetry** (Python dependency manager)
```bash
brew install poetry
poetry --version
```

✅ **Optional: Nevermined API Key** (for payment features)
- Sign up at https://nevermined.app
- Create API key in dashboard
- Create a pricing plan (credit-based)

## One-Command Startup

From the project root:

```bash
./restart-all.sh
```

This starts all 4 services automatically:
- WebDemo (8080)
- A2A Agent (9000)
- MCP Server (3000)
- Buyer Agent (8000)

**Expected output**:
```
Starting ComplianceShield services...
✅ WebDemo (8080) — http://localhost:8080
✅ A2A Agent (9000) — http://localhost:9000
✅ MCP Server (3000) — http://localhost:3000
✅ Buyer Agent (8000) — http://localhost:8000

All services ready!
```

## Manual Setup (if needed)

### Step 1: Install Dependencies

```bash
cd agents/seller-simple-agent
poetry install

cd ../mcp-server-agent
poetry install

cd ../buyer-simple-agent
poetry install
```

### Step 2: Configure Environment

Each service needs a `.env` file. Copy from examples:

```bash
cd agents/seller-simple-agent
cp .env.example .env
# Edit .env with your Nevermined API key (optional)
```

Key variables:
```bash
NVM_API_KEY=sandbox:your-key     # From nevermined.app
NVM_PLAN_ID=your-plan-id         # From nevermined.app
OPENAI_API_KEY=sk-your-key       # For LLM features
```

### Step 3: Start Services

In separate terminal windows:

**Terminal 1 — WebDemo + A2A Agent**:
```bash
cd agents/seller-simple-agent
poetry run python -m src.web
# Runs WebDemo on port 8080
# A2A Agent on port 9000 (auto-started)
```

**Terminal 2 — Buyer Agent**:
```bash
cd agents/buyer-simple-agent
poetry run python -m src.web --port 8000
```

**Terminal 3 — MCP Server**:
```bash
cd agents/mcp-server-agent
poetry run python -m src.server --port 3000
```

## Testing Services

### Test WebDemo
```bash
curl http://localhost:8080/api/scan \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"content": "This cream removes all wrinkles!"}'
```

Expected response: Compliance violations detected (FTC health claims)

### Test A2A Agent
```bash
curl http://localhost:9000/.well-known/agent.json | jq
```

Expected response: Agent metadata with available skills

### Test MCP Server
```bash
curl http://localhost:3000/health
```

Expected response: `{"status":"ok","service":"compliance-mcp-server"}`

### Test Buyer Agent
Open http://localhost:8000 in browser
- Should load React app
- Can interact with compliance features

## Next Steps

1. **Explore WebDemo**: http://localhost:8080
   - Test scanner with your own content
   - View compliance reports
   - Check pricing and features

2. **Try the API**:
   ```bash
   # Run a compliance scan
   curl http://localhost:8080/api/scan \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"content": "Your marketing copy here"}'
   ```

3. **Set up Nevermined** (optional):
   - Create account at https://nevermined.app
   - Add API key to `.env` files
   - Unlock paid features and payment integration

4. **Read the full docs**:
   - [README.md](../README.md) — Complete overview
   - [API Reference](./api-reference.md) — Endpoint documentation
   - [Compliance Rules](./compliance-rules.md) — What we check for

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9
```

### Module Not Found
```bash
# Ensure Poetry dependencies are installed
cd agents/seller-simple-agent
poetry install
```

### Environment Variables Missing
```bash
# Copy example and edit
cd agents/seller-simple-agent
cp .env.example .env
# Edit .env with your values
```

### Still Having Issues?

Check the detailed guides:
- [Getting Started Guide](./getting-started.md)
- [Deployment Guide](./deployment.md)
- [API Reference](./api-reference.md)

---

**That's it!** You should now have ComplianceShield running locally with all 4 services active.
