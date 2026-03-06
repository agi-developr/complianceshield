# ComplianceShield API Reference

Complete documentation for all 4 service APIs.

## Table of Contents

1. [WebDemo Scanner API](#webdemo-scanner-api) — REST endpoints
2. [A2A Agent API](#a2a-agent-api) — JSON-RPC with payments
3. [MCP Server API](#mcp-server-api) — Tool-based API
4. [Buyer Agent API](#buyer-agent-api) — Marketplace endpoints

---

## WebDemo Scanner API

**Base URL**: `http://localhost:8080`
**Protocol**: REST (JSON)
**Authentication**: None (open for demo)

### Endpoints

#### POST /api/scan

Scan content for compliance issues.

**Request**:
```json
{
  "content": "string (required) — Text to scan",
  "detail_level": "string (optional) — 'quick' (default), 'full', 'deep'"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "detail_level": "quick",
  "report": {
    "overall_risk": "LOW",
    "summary": "The provided content is minimal and generic...",
    "issues": [],
    "compliance_score": 95,
    "safe_sections": "The entire content...",
    "disclaimer": "This is AI-generated analysis..."
  },
  "report_id": "33d89058",
  "readable": "============================================================\n  COMPLIANCE REPORT — 🟢 Overall Risk: LOW\n...",
  "compliance_score": 95,
  "elapsed_seconds": 2.68
}
```

**Detail Levels**:
- `quick` (default): Basic risk assessment (1-3 sec)
- `full`: Per-claim analysis with scores (3-5 sec)
- `deep`: Full legal review with rewrite suggestions (5-10 sec)

**Example**:
```bash
# Quick scan
curl -X POST http://localhost:8080/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Our energy drink gives you instant energy!",
    "detail_level": "full"
  }'
```

**Response Fields**:
- `overall_risk`: Summary risk level (LOW, MEDIUM, HIGH)
- `compliance_score`: 0-100 score (100 = fully compliant)
- `issues[]`: Array of violations found
  - `type`: FTC, FDA, SEC, PRIVACY
  - `severity`: LOW, MEDIUM, HIGH
  - `claim`: The problematic text
  - `rule`: Applicable regulation
  - `suggestion`: How to fix it
- `safe_sections`: What passed compliance
- `readable`: Human-readable formatted report

#### GET /api/health

Health check endpoint.

**Response** (200 OK):
```json
{
  "status": "ok",
  "service": "compliance-scanner",
  "timestamp": "2026-03-06T22:14:10.150661Z",
  "uptime_seconds": 3600
}
```

#### GET /

Landing page (HTML).

**Response** (200 OK): HTML landing page with features, pricing, demo.

---

## A2A Agent API

**Base URL**: `http://localhost:9000`
**Protocol**: JSON-RPC 2.0
**Authentication**: Nevermined x402 (payment-signature header)

### Discovery

#### GET /.well-known/agent.json

Agent metadata for discovery.

**Response** (200 OK):
```json
{
  "name": "Compliance Checker Agent",
  "description": "AI-powered legal compliance checker for content creators...",
  "url": "http://localhost:9000",
  "version": "0.1.0",
  "skills": [
    {
      "id": "quick_scan",
      "name": "Quick Compliance Scan",
      "description": "Quick scan for legal compliance issues in content. Costs 1 credit.",
      "tags": ["compliance", "legal", "scan", "quick"]
    },
    {
      "id": "full_analysis",
      "name": "Full Compliance Analysis",
      "description": "Detailed compliance analysis with per-section risk scores. Costs 5 credits.",
      "tags": ["compliance", "legal", "analysis", "detailed"]
    },
    {
      "id": "deep_review",
      "name": "Deep Compliance Review",
      "description": "Comprehensive legal review with citations and rewrite suggestions. Costs 10 credits.",
      "tags": ["compliance", "legal", "review", "comprehensive"]
    },
    {
      "id": "scan_video",
      "name": "YouTube Video Compliance Scan",
      "description": "Analyze YouTube video transcripts for compliance issues. Costs 8 credits.",
      "tags": ["video", "compliance", "youtube", "transcripts"]
    }
  ],
  "pricing": "Credits vary by tool: quick_scan=1, full_analysis=5, deep_review=10, scan_video=8"
}
```

### JSON-RPC Methods

#### POST /

Submit JSON-RPC request with payment.

**Headers**:
```
Content-Type: application/json
payment-signature: {Nevermined_access_token}
```

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "quick_scan",
  "params": {
    "content": "Your content to scan"
  },
  "id": 1
}
```

**Response** (200 OK):
```json
{
  "jsonrpc": "2.0",
  "result": {
    "overall_risk": "LOW",
    "compliance_score": 95,
    "issues": [],
    "summary": "No compliance issues detected.",
    "report_id": "a1b2c3d4"
  },
  "id": 1
}
```

**Error Response** (402 Payment Required):
```json
{
  "error": {
    "code": -32001,
    "message": "Missing payment-signature header."
  },
  "id": 1
}
```

### Available Methods

#### quick_scan
**Cost**: 1 credit
**Speed**: 1-2 seconds

```json
{
  "jsonrpc": "2.0",
  "method": "quick_scan",
  "params": {
    "content": "Your content here"
  },
  "id": 1
}
```

#### full_analysis
**Cost**: 5 credits
**Speed**: 3-5 seconds

```json
{
  "jsonrpc": "2.0",
  "method": "full_analysis",
  "params": {
    "content": "Your content here"
  },
  "id": 1
}
```

Returns per-claim analysis:
```json
{
  "result": {
    "overall_risk": "MEDIUM",
    "claims": [
      {
        "claim": "Our product cures cancer",
        "type": "FDA",
        "severity": "HIGH",
        "suggestion": "Remove disease cure claims unless FDA-approved"
      }
    ],
    "report_id": "..."
  }
}
```

#### deep_review
**Cost**: 10 credits
**Speed**: 5-10 seconds

```json
{
  "jsonrpc": "2.0",
  "method": "deep_review",
  "params": {
    "content": "Your content here"
  },
  "id": 1
}
```

Returns comprehensive legal review with citations and rewrites.

#### scan_video
**Cost**: 8 credits
**Speed**: 2-4 seconds

```json
{
  "jsonrpc": "2.0",
  "method": "scan_video",
  "params": {
    "transcript": "Video transcript text here"
  },
  "id": 1
}
```

---

## MCP Server API

**Base URL**: `http://localhost:3000`
**Protocol**: Model Context Protocol (MCP)
**Authentication**: None (tool-based)

### Health Endpoint

#### GET /health

Service health check.

**Response** (200 OK):
```json
{
  "status": "ok",
  "service": "compliance-mcp-server",
  "timestamp": "2026-03-06T22:14:22.701065Z",
  "tools_available": 4
}
```

### MCP Tools

MCP tools are accessed as logical URLs. Use with Claude Desktop or compatible MCP clients.

#### scan-compliance

Quick compliance scan via MCP.

**URI**: `mcp://localhost:3000/tools/scan-compliance`

**Input**:
```json
{
  "content": "Text to scan"
}
```

**Output**:
```json
{
  "overall_risk": "LOW",
  "compliance_score": 95,
  "issues": []
}
```

#### analyze-claims

Extract and analyze individual claims.

**URI**: `mcp://localhost:3000/tools/analyze-claims`

**Input**:
```json
{
  "content": "Text with claims",
  "regulations": ["FTC", "FDA", "SEC"]
}
```

**Output**:
```json
{
  "claims": [
    {
      "claim": "Extracted claim text",
      "type": "FTC|FDA|SEC",
      "confidence": 0.95,
      "risk": "HIGH"
    }
  ]
}
```

#### research-regulations

Look up applicable regulations.

**URI**: `mcp://localhost:3000/tools/research-regulations`

**Input**:
```json
{
  "industry": "dietary_supplements",
  "regulation_type": "health_claims"
}
```

**Output**:
```json
{
  "regulations": [
    {
      "title": "Health Claims Rule",
      "reference": "16 CFR 101.72",
      "summary": "Rules for substantiated health claims..."
    }
  ]
}
```

#### generate-disclaimers

Create compliant disclaimers.

**URI**: `mcp://localhost:3000/tools/generate-disclaimers`

**Input**:
```json
{
  "content": "Product description",
  "regulation": "FDA"
}
```

**Output**:
```json
{
  "disclaimer": "These statements have not been evaluated by the FDA. This product is not intended to diagnose, treat, cure, or prevent any disease."
}
```

---

## Buyer Agent API

**Base URL**: `http://localhost:8000`
**Protocol**: REST (JSON)
**Frontend**: React 19 SPA

### Web Interface

#### GET /

React web application.

**Response** (200 OK): HTML with React app

### Available Features

- **Dashboard**: View compliance services and pricing
- **Scanner**: Test compliance on content
- **History**: View scan history and reports
- **Marketplace**: Discover agents and services

---

## Error Codes

### Common HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success | Scan completed |
| 402 | Payment Required | Missing payment signature |
| 400 | Bad Request | Invalid JSON |
| 404 | Not Found | Endpoint doesn't exist |
| 500 | Server Error | Internal service error |

### JSON-RPC Error Codes

| Code | Meaning |
|------|---------|
| -32000 | Server error |
| -32001 | Payment required |
| -32700 | Parse error |
| -32600 | Invalid request |
| -32601 | Method not found |
| -32602 | Invalid params |

---

## Rate Limiting

**WebDemo**: None (open for demo)
**A2A Agent**: Unlimited (credit-based pricing)
**MCP Server**: None (tool-based)
**Buyer Agent**: None (UI-based)

---

## Authentication

### Nevermined x402 (A2A Agent)

The `payment-signature` header contains a Nevermined access token:

```
payment-signature: Bearer {token}
```

Tokens are obtained from:
```
POST https://nevermined.app/api/v1/auth/token
```

With credentials:
```json
{
  "api_key": "sandbox:your-api-key",
  "plan_id": "your-plan-id"
}
```

---

## Examples

### Curl: WebDemo Scan

```bash
curl -X POST http://localhost:8080/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Try our miracle weight loss supplement! Lose 50 lbs in 30 days!",
    "detail_level": "full"
  }' | jq
```

### Python: A2A Agent Scan

```python
import requests
import json

token = "your_nevermined_token"

response = requests.post(
  "http://localhost:9000/",
  headers={
    "Content-Type": "application/json",
    "payment-signature": token
  },
  json={
    "jsonrpc": "2.0",
    "method": "quick_scan",
    "params": {"content": "Your content here"},
    "id": 1
  }
)

print(response.json())
```

### JavaScript: WebDemo Scan

```javascript
fetch('http://localhost:8080/api/scan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    content: 'Your content to scan',
    detail_level: 'full'
  })
})
.then(r => r.json())
.then(data => console.log(data.report))
```

---

**See Also**:
- [README](../README.md) — Project overview
- [Quick Start](./QUICK-START.md) — Get running in 5 minutes
- [Deployment](./deployment.md) — Production setup
