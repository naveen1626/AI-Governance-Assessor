from fastapi import APIRouter, HTTPException
from app.models import AssessRequest, Assessment, ResearchInput, AxisInfo, ResearchCategory
from app.services.risk_scorer import score_research
from app.services.governance import compute_tier, generate_llm_recommendations
from app.services.storage import add_assessment

router = APIRouter()


@router.post("/assess", response_model=Assessment)
async def assess_paper(request: AssessRequest):
    """Perform dual-use risk assessment on a research paper"""

    # Validate we have required content
    if not request.abstract.strip():
        raise HTTPException(status_code=400, detail="Abstract is required")

    # Score using LLM - category is auto-detected
    scores, axes_used, detected_category = await score_research(
        title=request.title,
        abstract=request.abstract,
        snippet=request.snippet
    )

    # Convert detected category string to enum (default to biomedical if not recognized)
    category_enum = None
    if detected_category:
        try:
            category_enum = ResearchCategory(detected_category)
        except ValueError:
            # Try to match common variations
            category_map = {
                "biomedical": ResearchCategory.BIOMEDICAL,
                "life_sciences": ResearchCategory.BIOMEDICAL,
                "semiconductor": ResearchCategory.SEMICONDUCTOR,
                "ai_hardware": ResearchCategory.SEMICONDUCTOR,
                "ai_ml": ResearchCategory.AI_ML,
                "ai": ResearchCategory.AI_ML,
                "ml": ResearchCategory.AI_ML,
                "machine_learning": ResearchCategory.AI_ML,
                "cybersecurity": ResearchCategory.CYBERSECURITY,
                "security": ResearchCategory.CYBERSECURITY,
                "chemistry": ResearchCategory.CHEMISTRY,
                "materials": ResearchCategory.CHEMISTRY,
                "nuclear": ResearchCategory.NUCLEAR,
                "radiological": ResearchCategory.NUCLEAR
            }
            category_enum = category_map.get(detected_category.lower())

    # Compute tier based on scores and metadata
    tier = compute_tier(scores, request.dissemination, request.audience)

    # Generate LLM-based recommendations considering category, risk, and regulations
    recommendations = await generate_llm_recommendations(
        title=request.title,
        abstract=request.abstract,
        category=detected_category,
        tier=tier,
        scores=scores
    )

    # Build assessment record
    research_input = ResearchInput(
        title=request.title,
        abstract=request.abstract,
        snippet=request.snippet,
        source_url=request.source_url,
        dissemination=request.dissemination,
        audience=request.audience,
        category=category_enum
    )

    # Convert axes to AxisInfo for storage
    axes_info = [
        AxisInfo(
            id=ax.id,
            name=ax.name,
            section=getattr(ax, 'section', None),
            reverse_scored=getattr(ax, 'reverse_scored', False)
        )
        for ax in axes_used
    ]

    assessment = Assessment(
        input=research_input,
        scores=scores,
        tier=tier,
        recommendations=recommendations,
        axes_used=axes_info
    )

    # Save to JSON
    add_assessment(assessment)

    return assessment
