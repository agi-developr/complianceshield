"""Setup script: registers the Compliance Checker agent and payment plan on Nevermined.

Only requires NVM_API_KEY in .env. Writes NVM_AGENT_ID and NVM_PLAN_ID back to .env.

Usage:
    poetry run python -m src.setup
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv, set_key
from payments_py import Payments, PaymentOptions
from payments_py.common.types import (
    AgentAPIAttributes,
    AgentMetadata,
    Endpoint,
    PlanMetadata,
)
from payments_py.plans import get_dynamic_credits_config, get_free_price_config

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(ENV_FILE)


def main():
    nvm_api_key = os.environ.get("NVM_API_KEY", "")
    nvm_environment = os.environ.get("NVM_ENVIRONMENT", "sandbox")

    if not nvm_api_key:
        print("Error: NVM_API_KEY is required. Set it in .env")
        sys.exit(1)

    existing_agent = os.environ.get("NVM_AGENT_ID", "")
    existing_plan = os.environ.get("NVM_PLAN_ID", "")
    if existing_agent and existing_plan:
        print(f"Already configured: agent={existing_agent[:16]}... plan={existing_plan[:16]}...")
        print("Re-registering with new IDs...")

    print(f"\nRegistering Compliance Checker on Nevermined ({nvm_environment})...\n")

    payments = Payments.get_instance(
        PaymentOptions(nvm_api_key=nvm_api_key, environment=nvm_environment)
    )

    agent_metadata = AgentMetadata(
        name="Compliance Checker Agent",
        description=(
            "AI-powered legal compliance checker for content creators. "
            "Analyzes scripts, transcripts, and posts for FTC, health, "
            "financial, privacy, and platform policy compliance issues. "
            "Three tiers: quick scan (1cr), full analysis (5cr), deep review (10cr)."
        ),
        tags=["compliance", "legal", "content-creator", "ftc", "youtube"],
    )

    agent_api = AgentAPIAttributes(
        endpoints=[
            Endpoint(verb="POST", url="https://compliance-checker.local/check"),
        ],
        agent_definition_url="https://compliance-checker.local/.well-known/agent.json",
    )

    plan_metadata = PlanMetadata(
        name="Compliance Checker - Credits Plan",
        description="Credits for compliance checking. Quick=1cr, Full=5cr, Deep=10cr.",
    )

    price_config = get_free_price_config()

    credits_config = get_dynamic_credits_config(
        credits_granted=100,
        min_credits_per_request=1,
        max_credits_per_request=10,
    )

    print("Calling register_agent_and_plan()...")
    result = payments.agents.register_agent_and_plan(
        agent_metadata=agent_metadata,
        agent_api=agent_api,
        plan_metadata=plan_metadata,
        price_config=price_config,
        credits_config=credits_config,
        access_limit="credits",
    )

    agent_id = result.get("agentId", "")
    plan_id = result.get("planId", "")

    if not agent_id or not plan_id:
        print(f"Error: unexpected response: {result}")
        sys.exit(1)

    print(f"\nRegistered successfully!")
    print(f"  Agent ID: {agent_id}")
    print(f"  Plan ID:  {plan_id}")

    if not ENV_FILE.exists():
        ENV_FILE.write_text(f"NVM_API_KEY={nvm_api_key}\nNVM_ENVIRONMENT={nvm_environment}\n")

    set_key(str(ENV_FILE), "NVM_AGENT_ID", agent_id)
    set_key(str(ENV_FILE), "NVM_PLAN_ID", plan_id)

    print(f"\nSaved to {ENV_FILE}")
    print("\nYou can now start the server:")
    print("  poetry run python -m src.agent        # HTTP mode")
    print("  poetry run python -m src.agent_a2a     # A2A mode")


if __name__ == "__main__":
    main()
