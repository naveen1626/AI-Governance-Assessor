import logging
from app.models import RiskScores, Tier, Dissemination, Audience

logger = logging.getLogger(__name__)


def compute_tier(scores: RiskScores, dissemination: Dissemination, audience: Audience) -> Tier:
    """
    Compute overall risk tier based on axis scores and metadata.

    Uses effective scores (with reverse scoring applied for safeguard axes).

    Rules:
    - Low: all effective scores <= 1
    - Medium: any effective score = 2, none = 3
    - High: any effective score = 3, but audience is experts only
    - Critical: any effective score = 3 AND broad/open dissemination or audience
    """
    # Get maximum effective score (reverse scoring already applied)
    max_score = scores.max_effective_score()

    # Check for broad access indicators
    is_broad_access = (
        dissemination == Dissemination.OPEN_SOURCE or
        audience == Audience.DEVELOPERS
    )

    is_expert_only = audience == Audience.EXPERTS

    if max_score <= 1:
        return Tier.LOW
    elif max_score == 2:
        return Tier.MEDIUM
    elif max_score == 3:
        if is_broad_access:
            return Tier.CRITICAL
        elif is_expert_only:
            return Tier.HIGH
        else:
            # Default to HIGH for score=3 cases
            return Tier.HIGH

    return Tier.MEDIUM  # Fallback


def get_recommendations(tier: Tier) -> list[str]:
    """Get default governance recommendations based on tier (fallback)"""
    recommendations = {
        Tier.LOW: [
            "Proceed with publication, no special review required.",
            "Standard internal documentation recommended."
        ],
        Tier.MEDIUM: [
            "Record assessment in internal tracking system.",
            "Internal governance review recommended before public release.",
            "Consider limiting technical details in public version."
        ],
        Tier.HIGH: [
            "Export-control / national-security review required before any external release.",
            "Default to internal-only preprint or limited distribution until reviewed.",
            "Consult with legal/compliance team on publication scope.",
            "Consider structured access controls for code/models."
        ],
        Tier.CRITICAL: [
            "Default NO open release of code, weights, or detailed methods.",
            "Escalate immediately to governance / export-control committee.",
            "Consider red-teaming and structured risk mitigation before any publication.",
            "Evaluate if publication should proceed at all.",
            "If proceeding, implement staged/gated release with monitoring."
        ]
    }
    return recommendations.get(tier, [])


# Government regulations reference by category
REGULATORY_FRAMEWORKS = {
    "biomedical": [
        "Dual Use Research of Concern (DURC) Policy (US HHS/NIH)",
        "Select Agent Regulations (42 CFR Part 73)",
        "Cartagena Protocol on Biosafety",
        "WHO Responsible Life Sciences Research Framework",
        "EU Regulation on dual-use items (2021/821)"
    ],
    "semiconductor": [
        "Export Administration Regulations (EAR) - Commerce Control List",
        "CHIPS and Science Act compliance requirements",
        "Wassenaar Arrangement (dual-use technology controls)",
        "Foreign Direct Product Rule (FDPR)",
        "EU Dual-Use Regulation (2021/821)"
    ],
    "ai_ml": [
        "EU AI Act (Regulation 2024/1689) - High-risk AI systems",
        "US Executive Order 14110 on Safe, Secure AI",
        "NIST AI Risk Management Framework (AI RMF 1.0)",
        "OECD AI Principles",
        "G7 Hiroshima AI Process Code of Conduct"
    ],
    "cybersecurity": [
        "Wassenaar Arrangement - Intrusion software controls",
        "Computer Fraud and Abuse Act (CFAA) considerations",
        "EU NIS2 Directive",
        "NIST Cybersecurity Framework",
        "Vulnerability disclosure frameworks (ISO 29147)"
    ],
    "chemistry": [
        "Chemical Weapons Convention (CWC) Schedule lists",
        "Export Administration Regulations (EAR) - Chemical precursors",
        "REACH Regulation (EU) for hazardous substances",
        "Responsible Science Framework for chemistry",
        "Australia Group export controls"
    ],
    "nuclear": [
        "Nuclear Regulatory Commission (NRC) Part 810 regulations",
        "Nuclear Non-Proliferation Treaty (NPT) obligations",
        "IAEA safeguards and Code of Conduct",
        "Nuclear Suppliers Group guidelines",
        "Export Administration Regulations - Nuclear technology"
    ]
}


def build_recommendations_prompt(
    title: str,
    abstract: str,
    category: str | None,
    tier: Tier,
    scores: RiskScores
) -> str:
    """Build prompt for LLM to generate contextual recommendations"""

    # Get relevant regulations for category
    regulations = REGULATORY_FRAMEWORKS.get(category, REGULATORY_FRAMEWORKS["ai_ml"])
    regulations_text = "\n".join(f"- {reg}" for reg in regulations)

    # Build axis scores summary
    high_risk_axes = []
    safeguard_gaps = []

    for axis_id, axis_score in scores.scores.items():
        effective_score = axis_score.score
        if axis_score.reverse_scored:
            effective_score = 3 - axis_score.score
            if effective_score >= 2:
                safeguard_gaps.append(f"{axis_id}: {axis_score.rationale[:100]}")
        else:
            if axis_score.score >= 2:
                high_risk_axes.append(f"{axis_id}: {axis_score.rationale[:100]}")

    risk_summary = ""
    if high_risk_axes:
        risk_summary += "High-risk axes:\n" + "\n".join(f"- {a}" for a in high_risk_axes[:3])
    if safeguard_gaps:
        risk_summary += "\n\nSafeguard gaps:\n" + "\n".join(f"- {g}" for g in safeguard_gaps[:2])

    prompt = f"""You are an AI governance expert. Based on the research paper assessment below, provide 2-3 specific, actionable governance recommendations that reference relevant government regulations and frameworks.

## Research Paper
**Title:** {title}
**Abstract:** {abstract[:500]}...

## Assessment Results
**Category:** {category or "General AI/Technology"}
**Risk Tier:** {tier.value}

{risk_summary}

## Relevant Regulatory Frameworks for {category or "this research"}:
{regulations_text}

## Instructions:
Generate exactly 2-3 specific recommendations that:
1. Address the identified risks and safeguard gaps
2. Reference specific regulations or frameworks from the list above
3. Provide actionable steps for governance compliance
4. Are appropriate for the {tier.value} risk level

Respond ONLY with a JSON array of 2-3 recommendation strings:
["recommendation 1", "recommendation 2", "recommendation 3"]
"""
    return prompt


def parse_recommendations_response(response_text: str) -> list[str]:
    """Parse LLM response to extract recommendations"""
    import json
    import re

    # Handle markdown code blocks
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        parts = response_text.split("```")
        if len(parts) >= 2:
            response_text = parts[1]

    response_text = response_text.strip()

    # Try direct JSON parse
    try:
        recommendations = json.loads(response_text)
        if isinstance(recommendations, list):
            return [str(r) for r in recommendations[:3]]
    except json.JSONDecodeError:
        pass

    # Try to find JSON array
    match = re.search(r'\[[\s\S]*?\]', response_text)
    if match:
        try:
            recommendations = json.loads(match.group(0))
            if isinstance(recommendations, list):
                return [str(r) for r in recommendations[:3]]
        except json.JSONDecodeError:
            pass

    # Fallback: extract quoted strings
    quotes = re.findall(r'"([^"]{20,})"', response_text)
    if quotes:
        return quotes[:3]

    return []


async def generate_llm_recommendations(
    title: str,
    abstract: str,
    category: str | None,
    tier: Tier,
    scores: RiskScores
) -> list[str]:
    """Generate contextual recommendations using LLM based on category, risk, and regulations"""
    from app.services.risk_scorer import call_llm

    prompt = build_recommendations_prompt(title, abstract, category, tier, scores)

    try:
        response_text = await call_llm(prompt)
        recommendations = parse_recommendations_response(response_text)

        if recommendations:
            logger.info(f"Generated {len(recommendations)} LLM recommendations")
            return recommendations
        else:
            logger.warning("Failed to parse LLM recommendations, using defaults")
            return get_recommendations(tier)

    except Exception as e:
        logger.error(f"LLM recommendation generation failed: {e}")
        return get_recommendations(tier)
