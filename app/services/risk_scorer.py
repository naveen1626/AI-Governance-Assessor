import json
import logging
from app.config import settings
from app.models import RiskScores, AxisScore, RiskAxis

logger = logging.getLogger(__name__)


def load_axes_config() -> dict:
    """Load axes configuration from JSON file"""
    try:
        with open(settings.axes_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"universal": True, "axes": []}


def get_universal_axes() -> list[RiskAxis]:
    """Get universal risk axes (applies to all categories)"""
    config = load_axes_config()

    if config.get("universal", False):
        axes_data = config.get("axes", [])
        return [RiskAxis(**ax) for ax in axes_data]

    # Fallback for old category-based config
    return get_fallback_axes()


def get_fallback_axes() -> list[RiskAxis]:
    """Fallback axes if config is invalid"""
    return [
        RiskAxis(id="A1", name="Dangerous Capability", question="Does this research enable dangerous capabilities?"),
        RiskAxis(id="B1", name="Accessibility", question="How accessible is this to non-experts?"),
        RiskAxis(id="C1", name="Safeguards", question="Are there adequate safeguards?", reverse_scored=True),
        RiskAxis(id="D1", name="Impact Scope", question="What is the potential harm scope?"),
    ]


def build_scoring_prompt(title: str, abstract: str, snippet: str | None, axes: list[RiskAxis]) -> str:
    """Build the LLM prompt for risk scoring with category detection"""

    # Group axes by section for clearer presentation
    axes_text = ""
    current_section = None

    for a in axes:
        section = getattr(a, 'section', None)
        if section and section != current_section:
            sections_map = {
                "A": "Capability and Domain",
                "B": "Accessibility and Diffusion",
                "C": "Safeguards and Governance",
                "D": "Impact Scope",
                "E": "Uncertainty and Ambiguity",
                "F": "Regulatory Controls"
            }
            section_name = sections_map.get(section, section)
            axes_text += f"\n### Section {section}: {section_name}\n"
            current_section = section

        reverse_note = " [NOTE: Higher score = BETTER safeguards = LOWER risk]" if getattr(a, 'reverse_scored', False) else ""
        axes_text += f"- **{a.id} - {a.name}**: {a.question}{reverse_note}\n"

    content_text = f"**Title:** {title}\n\n**Abstract:** {abstract}"
    if snippet:
        content_text += f"\n\n**Methods/Contributions Snippet:** {snippet}"

    # Build axis IDs for JSON template
    axis_ids = [a.id for a in axes]
    json_template = ",\n    ".join([f'"{aid}": {{"score": <0-3>, "rationale": "<explanation>"}}' for aid in axis_ids])

    prompt = f"""You are a dual-use risk assessor for research papers. Analyze the following research paper, identify its research category, and score it on each risk axis.

## Research Categories (pick the most appropriate one):
- **biomedical** - Biomedical / Life Sciences (CRISPR, gene editing, drug discovery, pathogens, etc.)
- **semiconductor** - Semiconductor / AI Hardware (chip design, EDA, accelerators, etc.)
- **ai_ml** - AI / Machine Learning (LLMs, training methods, model architectures, etc.)
- **cybersecurity** - Cybersecurity / AI Security (vulnerabilities, exploits, adversarial attacks, etc.)
- **chemistry** - Chemistry / Materials Science (synthesis, energetic materials, novel compounds, etc.)
- **nuclear** - Nuclear / Radiological (reactors, fuel cycles, radiation, etc.)

## Scoring Rubric (0-3 for each axis):
- **0** - Not relevant / clearly benign / strong controls in place
- **1** - Weak signal, indirect concern, or minor gap
- **2** - Meaningful concern but mitigated by context or expertise requirements
- **3** - Strong, direct concern that substantially raises risk profile

**Important:** For axes marked with [BETTER safeguards = LOWER risk], a score of 3 means EXCELLENT safeguards are present.

## Risk Axes to Evaluate:
{axes_text}

## Research Paper Content:
{content_text}

## Instructions:
1. First, identify the most appropriate research category from the list above
2. For each axis, provide a score from 0-3 and a brief rationale (1-2 sentences)

Respond ONLY with valid JSON in this exact format:
{{
    "category": "<category_id>",
    {json_template}
}}
"""
    return prompt


def parse_llm_response(response_text: str, axes: list[RiskAxis]) -> tuple[RiskScores, str | None]:
    """Parse JSON response from LLM into RiskScores and detected category"""
    import re

    logger.info(f"Raw LLM response (first 500 chars): {response_text[:500]}")

    axis_ids = [a.id for a in axes]
    axis_reverse_map = {a.id: getattr(a, 'reverse_scored', False) for a in axes}

    # Handle potential markdown code blocks
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        parts = response_text.split("```")
        if len(parts) >= 2:
            response_text = parts[1]

    response_text = response_text.strip()

    # First attempt: direct JSON parse
    try:
        scores_data = json.loads(response_text)
        category = scores_data.pop("category", None)
        logger.info(f"Parsed category from JSON: {category}")
        return build_risk_scores(scores_data, axis_ids, axis_reverse_map), category
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Direct JSON parse failed: {e}")

    # Second attempt: find and clean JSON object
    match = re.search(r'\{[\s\S]*\}', response_text)
    # print(response_text)
    if match:
        json_str = match.group(0)
        # Remove control characters
        json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', json_str)
        # print(json_str)

        try:
            scores_data = json.loads(json_str)
            category = scores_data.pop("category", None)
            # print(category)
            logger.info(f"Parsed category (2nd attempt): {category}")
            return build_risk_scores(scores_data, axis_ids, axis_reverse_map), category
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Second JSON parse attempt failed: {e}")

        # Third attempt: regex extraction
        # Try to extract category with regex
        cat_match = re.search(r'"category"\s*:\s*"([^"]+)"', json_str)
        print(cat_match)
        category = cat_match.group(1) if cat_match else None
        print(category)
        logger.info(f"Parsed category (regex): {category}")

        scores_data = extract_scores_with_regex(json_str, axis_ids)
        return build_risk_scores(scores_data, axis_ids, axis_reverse_map), category

    # No JSON found at all - return defaults
    return build_default_scores(axis_ids, axis_reverse_map, "No valid JSON found in LLM response"), None


def build_risk_scores(scores_data: dict, axis_ids: list[str], axis_reverse_map: dict) -> RiskScores:
    """Build RiskScores from parsed data with defaults for missing keys"""
    scores_dict = {}

    for axis_id in axis_ids:
        if axis_id in scores_data:
            data = scores_data[axis_id]
            scores_dict[axis_id] = AxisScore(
                score=data.get("score", 0),
                rationale=data.get("rationale", "No rationale provided"),
                reverse_scored=axis_reverse_map.get(axis_id, False)
            )
        else:
            scores_dict[axis_id] = AxisScore(
                score=0,
                rationale=f"Missing {axis_id} from response",
                reverse_scored=axis_reverse_map.get(axis_id, False)
            )

    return RiskScores(scores=scores_dict)


def build_default_scores(axis_ids: list[str], axis_reverse_map: dict, error_msg: str) -> RiskScores:
    """Build default RiskScores with error message"""
    scores_dict = {}
    for axis_id in axis_ids:
        scores_dict[axis_id] = AxisScore(
            score=0,
            rationale=error_msg,
            reverse_scored=axis_reverse_map.get(axis_id, False)
        )
    return RiskScores(scores=scores_dict)


def extract_scores_with_regex(json_str: str, axis_ids: list[str]) -> dict:
    """Extract scores from malformed JSON using regex"""
    import re

    scores_data = {}

    for axis_id in axis_ids:
        # Find the start of this axis block
        axis_start = re.search(rf'"{axis_id}"\s*:\s*\{{', json_str)
        if not axis_start:
            scores_data[axis_id] = {"score": 0, "rationale": f"Could not find {axis_id} in response"}
            continue

        start_pos = axis_start.end()

        # Extract score
        score_match = re.search(r'"score"\s*:\s*(\d)', json_str[start_pos:start_pos+50])
        score = int(score_match.group(1)) if score_match else 0

        # Find rationale
        rationale_start = json_str.find('"rationale"', start_pos)
        if rationale_start == -1:
            rationale = "Could not find rationale"
        else:
            quote_start = json_str.find('"', rationale_start + len('"rationale"') + 1)
            if quote_start == -1:
                rationale = "Could not parse rationale"
            else:
                pos = quote_start + 1
                while pos < len(json_str):
                    if json_str[pos] == '"' and json_str[pos-1] != '\\':
                        break
                    pos += 1
                rationale = json_str[quote_start+1:pos]
                rationale = rationale.replace('\\"', '"').replace('\\n', ' ').replace('\\t', ' ')

        scores_data[axis_id] = {"score": score, "rationale": rationale}

    return scores_data


async def call_anthropic(prompt: str) -> str:
    """Call Anthropic Claude API"""
    from anthropic import Anthropic

    client = Anthropic(api_key=settings.get_api_key())
    message = client.messages.create(
        model=settings.llm_model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


async def call_openai(prompt: str) -> str:
    """Call OpenAI API"""
    from openai import OpenAI

    client = OpenAI(api_key=settings.get_api_key())
    response = client.chat.completions.create(
        model=settings.llm_model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


async def call_google(prompt: str) -> str:
    """Call Google Gemini API"""
    import google.generativeai as genai

    genai.configure(api_key=settings.get_api_key())
    model = genai.GenerativeModel(settings.llm_model)
    response = model.generate_content(prompt)
    return response.text


async def call_groq(prompt: str) -> str:
    """Call Groq API (uses OpenAI-compatible interface)"""
    from openai import OpenAI

    client = OpenAI(
        api_key=settings.get_api_key(),
        base_url="https://api.groq.com/openai/v1"
    )
    response = client.chat.completions.create(
        model=settings.llm_model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


async def call_together(prompt: str) -> str:
    """Call Together AI API (uses OpenAI-compatible interface)"""
    from openai import OpenAI

    client = OpenAI(
        api_key=settings.get_api_key(),
        base_url="https://api.together.xyz/v1"
    )
    response = client.chat.completions.create(
        model=settings.llm_model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


async def call_llm(prompt: str) -> str:
    """Call the configured LLM provider"""
    provider = settings.llm_provider

    if not settings.get_api_key():
        raise ValueError(f"No API key configured for provider: {provider}")

    if provider == "anthropic":
        return await call_anthropic(prompt)
    elif provider == "openai":
        return await call_openai(prompt)
    elif provider == "google":
        return await call_google(prompt)
    elif provider == "groq":
        return await call_groq(prompt)
    elif provider == "together":
        return await call_together(prompt)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


async def detect_category(title: str, abstract: str) -> str | None:
    """Detect research category using a simple LLM call"""
    prompt = f"""Classify this research paper into ONE of these categories. Respond with ONLY the category ID, nothing else.

Categories:
- biomedical (Biomedical / Life Sciences: CRISPR, gene editing, drug discovery, pathogens)
- semiconductor (Semiconductor / AI Hardware: chip design, EDA, accelerators)
- ai_ml (AI / Machine Learning: LLMs, training methods, model architectures)
- cybersecurity (Cybersecurity: vulnerabilities, exploits, adversarial attacks)
- chemistry (Chemistry / Materials Science: synthesis, energetic materials, novel compounds)
- nuclear (Nuclear / Radiological: reactors, fuel cycles, radiation)

Paper Title: {title}
Paper Abstract: {abstract[:1000]}

Category ID:"""

    try:
        response = await call_llm(prompt)
        # Extract just the category ID
        response = response.strip().lower()
        valid_categories = ["biomedical", "semiconductor", "ai_ml", "cybersecurity", "chemistry", "nuclear"]

        # Check if response contains a valid category
        for cat in valid_categories:
            if cat in response:
                logger.info(f"Detected category via simple prompt: {cat}")
                return cat

        logger.warning(f"Could not detect category from response: {response}")
        return None
    except Exception as e:
        logger.error(f"Category detection failed: {e}")
        return None


async def score_research(
    title: str,
    abstract: str,
    snippet: str | None = None
) -> tuple[RiskScores, list[RiskAxis], str | None]:
    """Score research paper using configured LLM

    Returns tuple of (scores, axes_used, detected_category)
    Category is auto-detected by LLM from paper content
    """
    axes = get_universal_axes()
    prompt = build_scoring_prompt(title, abstract, snippet, axes)

    try:
        response_text = await call_llm(prompt)
        scores, detected_category = parse_llm_response(response_text, axes)
        logger.info(f"Detected category from main response: {detected_category}")

        # If category wasn't detected in main response, try a separate call
        if not detected_category:
            logger.info("Category not found in main response, trying separate detection...")
            detected_category = await detect_category(title, abstract)

        logger.info(f"Final detected category: {detected_category}")
        return scores, axes, detected_category
    except Exception as e:
        axis_ids = [a.id for a in axes]
        axis_reverse_map = {a.id: getattr(a, 'reverse_scored', False) for a in axes}
        scores = build_default_scores(axis_ids, axis_reverse_map, f"LLM call failed: {str(e)}")
        return scores, axes, None
