"""
Autonomous buyer agent — discovers ALL marketplace agents and calls them.

This is the key missing piece for hackathon scoring! The existing client.py
only calls a hardcoded localhost URL, missing all other agents.

This module discovers agents via the Nevermined REST API:
  GET /api/v1/protocol/all-plans        -> all plans across the platform
  GET /api/v1/protocol/plans/{id}/agents -> agents linked to each plan

Then it buys credits and calls each agent, maximizing:
  - Plans bought  (x4 multiplier)
  - Calls made    (x4 multiplier)  
  - Diversity: unique counterparties (x3, cap 20)

Usage:
    # Set your .env with NVM_API_KEY, NVM_PLAN_ID
    poetry run python -m src.autonomous_discovery
    
    # Or with custom settings:
    BUYER_MAX_ROUNDS=20 BUYER_PER_ROUND=50 poetry run python -m src.autonomous_discovery
"""

import asyncio
import os
import random
import sys
import warnings

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

from dotenv import load_dotenv
load_dotenv()

import httpx
from payments_py import Payments, PaymentOptions

NVM_API_KEY = os.getenv("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.getenv("NVM_ENVIRONMENT", "sandbox")

if not NVM_API_KEY:
    print("ERROR: NVM_API_KEY is required in .env")
    sys.exit(1)

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
)

# Nevermined sandbox REST API
NVM_API_BASE = "https://api.sandbox.nevermined.app/api/v1/protocol"

# Your own IDs — skip during discovery to avoid calling yourself
OWN_AGENT_ID = os.getenv("NVM_AGENT_ID", "")
OWN_PLAN_ID = os.getenv("NVM_PLAN_ID", "")

# Sample queries to send to agents
SAMPLE_QUERIES = [
    "Latest advances in AI agents and autonomous systems",
    "Compliance automation with machine learning",
    "Creator economy legal frameworks 2026",
    "AI-powered contract analysis trends",
    "Decentralized AI marketplaces overview",
    "Multi-agent systems for business automation",
    "AI safety and governance frameworks",
    "Blockchain-based reputation systems",
    "Privacy-preserving AI techniques",
    "Autonomous legal compliance checking",
]


def _extract_post_urls(endpoints: list, base_url: str = "") -> list[str]:
    """Extract callable POST URLs from agent endpoint definitions.

    Handles two formats found in the API:
      - Format 1: {"POST": "https://url"}
      - Format 2: {"url": "https://url", "verb": "POST"}
    """
    urls: list[str] = []
    for ep in endpoints:
        if not isinstance(ep, dict):
            continue
        # Format 1: {"POST": "https://..."} — HTTP method as key
        for method in ("POST", "post", "Post"):
            if method in ep:
                url = ep[method]
                if isinstance(url, str) and url.startswith("http"):
                    urls.append(url)
        # Format 2: {"url": "...", "verb": "POST"}
        url = ep.get("url", "")
        verb = ep.get("verb", ep.get("method", "")).upper()
        if verb == "POST" and isinstance(url, str):
            if url.startswith("http"):
                urls.append(url)
            elif base_url and base_url.startswith("http") and url.startswith("/"):
                urls.append(f"{base_url.rstrip('/')}{url}")
    return list(dict.fromkeys(urls))  # dedupe preserving order


async def discover_agents() -> list[dict]:
    """Discover ALL agents via the Nevermined protocol REST API.

    This is the key function that was missing! It:
      1. GET /all-plans -> paginated list of ALL plans on the platform
      2. Filters active/listed plans, skips our own
      3. GET /plans/{planId}/agents -> agents linked to each plan
      4. Returns deduplicated list of callable agents
    """
    discovered: list[dict] = []
    seen_ids: set[str] = set()
    headers = {"Authorization": f"Bearer {NVM_API_KEY}"}

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Step 1: Paginate through ALL plans
        all_plans: list[dict] = []
        page = 1
        while True:
            resp = await client.get(
                f"{NVM_API_BASE}/all-plans",
                params={"page": page, "offset": 100},
                headers=headers,
            )
            if resp.status_code != 200:
                print(f"  [Discovery] all-plans page {page} -> {resp.status_code}")
                break
            data = resp.json()
            plans = data.get("plans", [])
            all_plans.extend(plans)
            total = data.get("total", 0)
            print(f"  [Discovery] Page {page}: {len(plans)} plans (total: {total})")
            if len(all_plans) >= total or not plans:
                break
            page += 1

        # Step 2: Filter plans (skip ours, skip deactivated)
        candidates: list[dict] = []
        for plan in all_plans:
            pid = plan.get("id", "")
            if pid == OWN_PLAN_ID:
                continue
            name = plan.get("metadata", {}).get("main", {}).get("name", "")
            if "DEACTIVATED" in name.upper():
                continue
            candidates.append(plan)

        print(f"  [Discovery] {len(candidates)} candidate plans (of {len(all_plans)} total)")

        # Step 3: Fetch agents for each plan (concurrent, rate-limited)
        sem = asyncio.Semaphore(10)

        async def _fetch(plan: dict):
            pid = plan.get("id", "")
            async with sem:
                try:
                    r = await client.get(
                        f"{NVM_API_BASE}/plans/{pid}/agents",
                        headers=headers,
                    )
                    if r.status_code != 200:
                        return
                    for agent in r.json().get("agents", []):
                        aid = agent.get("id", "")
                        if not aid or aid == OWN_AGENT_ID or aid in seen_ids:
                            continue
                        meta = agent.get("metadata", {})
                        name = meta.get("main", {}).get("name", "Unknown")
                        if "DEACTIVATED" in name.upper():
                            continue
                        agent_meta = meta.get("agent", {})
                        seen_ids.add(aid)
                        discovered.append({
                            "agent_id": aid,
                            "name": name,
                            "plan_id": pid,
                            "endpoints": agent_meta.get("endpoints", []),
                            "base_url": agent_meta.get("agentDefinitionUrl", ""),
                        })
                except Exception:
                    pass

        await asyncio.gather(*[_fetch(p) for p in candidates], return_exceptions=True)

    with_urls = sum(1 for a in discovered if _extract_post_urls(a["endpoints"], a["base_url"]))
    print(f"  [Discovery] {len(discovered)} agents ({with_urls} with POST endpoints)")
    return discovered


async def buy_plan_and_call(agent_info: dict, query: str) -> dict:
    """Buy a plan from an agent and make a call to it."""
    agent_id = agent_info["agent_id"]
    name = agent_info["name"]
    plan_id = agent_info.get("plan_id", "")
    base_url = agent_info.get("base_url", "")

    if not plan_id:
        return {"success": False, "reason": "No plan_id", "agent": name}

    headers = {
        "Authorization": f"Bearer {NVM_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Step 1: Order the plan
            print(f"  [Buy] {name} (plan={plan_id[:30]}...)")
            try:
                order_resp = await client.post(
                    f"{NVM_API_BASE}/plans/{plan_id}/order",
                    headers=headers,
                )
                if order_resp.status_code == 200:
                    print(f"  [Buy] OK: {order_resp.text[:80]}")
                else:
                    msg = order_resp.text[:80]
                    if "already" in msg.lower() or "subscrib" in msg.lower():
                        print(f"  [Buy] Already subscribed")
                    else:
                        print(f"  [Buy] {order_resp.status_code}: {msg}")
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout):
                print(f"  [Buy] Order timeout/connect error")

            # Step 2: Get x402 access token
            try:
                token_resp = await client.get(
                    f"{NVM_API_BASE}/token/{plan_id}/{agent_id}",
                    headers=headers,
                )
                if token_resp.status_code != 200:
                    print(f"  [Token] HTTP {token_resp.status_code}: {token_resp.text[:80]}")
                    return {"success": False, "reason": f"Token HTTP {token_resp.status_code}", "agent": name}
                token_data = token_resp.json()
                token = token_data.get("accessToken", token_data.get("token", ""))
            except Exception as e:
                print(f"  [Token] Error: {str(e)[:100]}")
                return {"success": False, "reason": str(e)[:100], "agent": name}

            if not token:
                print(f"  [Token] Empty")
                return {"success": False, "reason": "No access token", "agent": name}

            # Step 3: Call the agent endpoint with payment signature
            urls = _extract_post_urls(agent_info.get("endpoints", []), base_url)
            if not urls and base_url and base_url.startswith("http"):
                # Fallback: try common endpoint patterns
                for p in ["/ask", "/query", "/search", "/prompt", "/run", "/data"]:
                    urls.append(f"{base_url.rstrip('/')}{p}")

            if not urls:
                return {"success": False, "reason": "No URLs", "agent": name}

            for url in urls:
                try:
                    resp = await client.post(
                        url,
                        json={"query": query},
                        headers={
                            "Content-Type": "application/json",
                            "payment-signature": token,
                        },
                    )
                    print(f"  [Call] {name} @ {url} -> {resp.status_code}")
                    if resp.status_code in (200, 201, 202):
                        return {
                            "success": True,
                            "status_code": resp.status_code,
                            "agent": name,
                            "agent_id": agent_id,
                            "url": url,
                        }
                    if resp.status_code < 500:
                        return {
                            "success": False,
                            "status_code": resp.status_code,
                            "agent": name,
                        }
                except httpx.ConnectError:
                    print(f"  [Call] No connect: {url}")
                except httpx.ReadTimeout:
                    print(f"  [Call] Timeout: {url}")
                except Exception as e:
                    print(f"  [Call] Error: {e}")

        return {"success": False, "reason": "All endpoints failed", "agent": name}

    except Exception as e:
        print(f"  [Error] {name}: {e}")
        return {"success": False, "reason": str(e)[:200], "agent": name}


async def run_autonomous_buyer(
    max_rounds: int = 10,
    delay: int = 30,
    per_round: int = 40,
):
    """Main buyer loop — discover ALL agents, buy, call, repeat."""
    print(f"\n{'='*60}")
    print("  Autonomous Buyer Agent (Marketplace Discovery)")
    print(f"{'='*60}")
    print(f"  Rounds: {max_rounds} | Per-round: {per_round} | Delay: {delay}s")
    print(f"{'='*60}\n")

    called: set[str] = set()
    total = 0
    ok = 0
    bought = 0
    cached_agents: list[dict] = []

    for rnd in range(1, max_rounds + 1):
        print(f"\n--- Round {rnd}/{max_rounds} ---")

        # Re-discover every 3 rounds to find new agents
        if not cached_agents or rnd % 3 == 1:
            cached_agents = await discover_agents()

        if not cached_agents:
            print("[!] No agents found, waiting...")
            await asyncio.sleep(delay)
            continue

        # Prioritize uncalled agents (diversity scoring: x3, cap 20)
        uncalled = [a for a in cached_agents if a["agent_id"] not in called]
        already = [a for a in cached_agents if a["agent_id"] in called]
        batch = (uncalled + already)[:per_round]
        print(f"[Batch] {len(batch)} agents ({len(uncalled)} new)")

        for info in batch:
            aid = info["agent_id"]
            result = await buy_plan_and_call(info, random.choice(SAMPLE_QUERIES))
            total += 1
            if result.get("success"):
                ok += 1
            if aid not in called:
                called.add(aid)
                bought += 1
                print(f"  [NEW] #{len(called)}: {info['name']}")
            await asyncio.sleep(1)

        print(f"\n[Stats] Total: {total} | OK: {ok} | Unique: {len(called)} | Round: {rnd}")

        if rnd < max_rounds:
            print(f"[Wait] {delay}s...")
            await asyncio.sleep(delay)

    print(f"\n{'='*60}")
    print(f"  DONE — calls={total} ok={ok} unique={len(called)} bought={bought}")
    print(f"{'='*60}\n")


def main():
    max_rounds = int(os.getenv("BUYER_MAX_ROUNDS", "10"))
    delay = int(os.getenv("BUYER_DELAY", "30"))
    per_round = int(os.getenv("BUYER_PER_ROUND", "40"))
    asyncio.run(run_autonomous_buyer(max_rounds=max_rounds, delay=delay, per_round=per_round))


if __name__ == "__main__":
    main()
