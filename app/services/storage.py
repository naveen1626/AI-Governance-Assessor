import json
from pathlib import Path
from app.models import Assessment, AssessmentsStore
from app.config import settings


def ensure_data_dir():
    """Ensure data directory exists"""
    settings.data_dir.mkdir(parents=True, exist_ok=True)


def load_assessments() -> AssessmentsStore:
    """Load all assessments from JSON file"""
    ensure_data_dir()
    if not settings.assessments_file.exists():
        return AssessmentsStore(assessments=[])

    with open(settings.assessments_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return AssessmentsStore.model_validate(data)


def save_assessments(store: AssessmentsStore):
    """Save assessments to JSON file"""
    ensure_data_dir()
    with open(settings.assessments_file, "w", encoding="utf-8") as f:
        json.dump(store.model_dump(mode="json"), f, indent=2, default=str)


def add_assessment(assessment: Assessment) -> Assessment:
    """Add a new assessment and save"""
    store = load_assessments()
    store.assessments.insert(0, assessment)  # Most recent first
    save_assessments(store)
    return assessment


def get_assessment(assessment_id: str) -> Assessment | None:
    """Get a single assessment by ID"""
    store = load_assessments()
    for a in store.assessments:
        if a.id == assessment_id:
            return a
    return None


def get_all_assessments() -> list[Assessment]:
    """Get all assessments"""
    store = load_assessments()
    return store.assessments
