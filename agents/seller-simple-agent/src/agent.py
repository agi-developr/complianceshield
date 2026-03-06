"""
FastAPI server for the Compliance Checker agent.

Payment protection is handled by @requires_payment on the tools.

Usage:
    poetry run agent
"""

import base64
import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from payments_py.x402.strands import extract_payment_required

from .analytics import analytics
from .pricing import PRICING_TIERS
from .strands_agent import NVM_PLAN_ID, create_agent

PORT = int(os.getenv("PORT", "3000"))


def _create_model():
    """Create the Strands model — Anthropic, Bedrock, or OpenAI."""
    provider = os.getenv("COMPLIANCE_LLM_PROVIDER", "openai")
    if provider == "bedrock":
        from strands.models.bedrock import BedrockModel
        return BedrockModel(
            model_id=os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"),
            region_name=os.getenv("AWS_REGION", "us-west-2"),
        )
    elif provider == "anthropic":
        from strands.models.anthropic import AnthropicModel
        return AnthropicModel(
            client_args={"api_key": os.environ.get("ANTHROPIC_API_KEY", "")},
            model_id=os.getenv("COMPLIANCE_MODEL_ID", "claude-haiku-4-5-20251001"),
            max_tokens=4096,
        )
    else:
        from strands.models.openai import OpenAIModel
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            print("OPENAI_API_KEY is required when using OpenAI provider.")
            sys.exit(1)
        return OpenAIModel(
            client_args={"api_key": api_key},
            model_id=os.getenv("MODEL_ID", "gpt-4o-mini"),
        )


model = _create_model()
agent = create_agent(model)

app = FastAPI(
    title="Compliance Checker Agent",
    description="AI-powered legal compliance checking for content creators. "
    "Analyzes scripts, transcripts, and posts for FTC, health, financial, "
    "and privacy compliance issues.",
)


class ComplianceRequest(BaseModel):
    content: str
    detail_level: str = "quick"


@app.post("/check")
async def check(request: Request, body: ComplianceRequest) -> JSONResponse:
    """Check content for compliance issues.

    Send content with a payment token to get a compliance report.
    """
    try:
        payment_token = request.headers.get("payment-signature", "")
        state = {"payment_token": payment_token} if payment_token else {}

        # Route to appropriate tool based on detail level
        prompt_map = {
            "quick": f"Quick scan this content for compliance issues:\n\n{body.content}",
            "full": f"Do a full compliance analysis of this content:\n\n{body.content}",
            "deep": f"Do a deep compliance review with legal citations:\n\n{body.content}",
        }
        prompt = prompt_map.get(body.detail_level, prompt_map["quick"])

        result = agent(prompt, invocation_state=state)

        # Check if payment was required but not fulfilled
        payment_required = extract_payment_required(agent.messages)
        if payment_required and not state.get("payment_settlement"):
            encoded = base64.b64encode(
                json.dumps(payment_required).encode()
            ).decode()
            return JSONResponse(
                status_code=402,
                content={
                    "error": "Payment Required",
                    "message": str(result),
                },
                headers={"payment-required": encoded},
            )

        # Success
        settlement = state.get("payment_settlement")
        credits = int(settlement.credits_redeemed) if settlement else 0
        analytics.record_request(body.detail_level, credits)

        return JSONResponse(content={
            "response": str(result),
            "credits_used": credits,
            "detail_level": body.detail_level,
        })

    except Exception as error:
        print(f"Error in /check: {error}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )


@app.post("/data")
async def data(request: Request, body: ComplianceRequest) -> JSONResponse:
    """Alias for /check — backward compatibility with buyer agents."""
    return await check(request, body)


@app.get("/pricing")
async def pricing() -> JSONResponse:
    """Get pricing information."""
    return JSONResponse(content={
        "planId": NVM_PLAN_ID,
        "tiers": PRICING_TIERS,
    })


@app.get("/stats")
async def stats() -> JSONResponse:
    """Get usage statistics."""
    return JSONResponse(content=analytics.get_stats())


@app.get("/health")
async def health() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(content={"status": "ok", "service": "compliance-checker"})


def main():
    """Run the FastAPI server."""
    print(f"\n{'='*60}")
    print(f"  ⚖️  COMPLIANCE CHECKER AGENT")
    print(f"  Running on http://localhost:{PORT}")
    print(f"{'='*60}")
    print(f"\nPlan ID: {NVM_PLAN_ID}")
    print(f"\nEndpoints:")
    print(f"  POST /check    - Check content for compliance (x402 token required)")
    print(f"  POST /data     - Alias for /check")
    print(f"  GET  /pricing  - View pricing tiers")
    print(f"  GET  /stats    - View usage analytics")
    print(f"  GET  /health   - Health check")
    print(f"\nPricing:")
    for tier, info in PRICING_TIERS.items():
        print(f"  {tier}: {info['credits']} credits - {info['description']}")
    print()

    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
