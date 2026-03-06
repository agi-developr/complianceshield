"""Pricing tiers for the compliance checker agent."""

PRICING_TIERS = {
    "quick": {
        "credits": 1,
        "description": "Quick compliance scan - flags obvious legal issues in content",
        "tool": "quick_scan",
    },
    "full": {
        "credits": 5,
        "description": "Full compliance analysis - detailed per-section report with risk scores",
        "tool": "full_analysis",
    },
    "deep": {
        "credits": 10,
        "description": "Deep compliance review - full analysis + legal citations + edit suggestions",
        "tool": "deep_review",
    },
}


def get_credits_for_complexity(complexity: str) -> int:
    """Return the credit cost for a given complexity tier."""
    tier = PRICING_TIERS.get(complexity, PRICING_TIERS["quick"])
    return tier["credits"]
