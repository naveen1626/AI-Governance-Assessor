from fastapi import APIRouter, HTTPException
from app.models import Assessment
from app.services.storage import get_all_assessments, get_assessment

router = APIRouter()


@router.get("/history", response_model=list[Assessment])
async def list_assessments():
    """Get all past assessments"""
    return get_all_assessments()


@router.get("/history/{assessment_id}", response_model=Assessment)
async def get_assessment_by_id(assessment_id: str):
    """Get a single assessment by ID"""
    assessment = get_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment
