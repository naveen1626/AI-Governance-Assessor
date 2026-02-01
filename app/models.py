from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class Dissemination(str, Enum):
    INTERNAL = "Internal only"
    PREPRINT = "Preprint / arXiv only"
    CONFERENCE = "Conference / journal"
    OPEN_SOURCE = "Open-source code + weights"


class Audience(str, Enum):
    GOVERNANCE = "Governance auditor"
    DEVELOPERS = "Broad developer community"
    EXPORT_CONTROL = "Export control reviewer"
    EXPERTS = "Domain experts only"


class ResearchCategory(str, Enum):
    SEMICONDUCTOR = "semiconductor"
    BIOMEDICAL = "biomedical"
    CYBERSECURITY = "cybersecurity"
    AI_ML = "ai_ml"
    CHEMISTRY = "chemistry"
    NUCLEAR = "nuclear"


class Tier(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ResearchInput(BaseModel):
    """Input from user - either URL or manual entry"""
    title: str
    abstract: str
    snippet: Optional[str] = None
    source_url: Optional[str] = None
    dissemination: Dissemination
    audience: Audience
    category: Optional[ResearchCategory] = None  # Auto-detected by LLM


class AxisScore(BaseModel):
    """Score for a single risk axis"""
    score: int = Field(ge=0, le=3)
    rationale: str
    reverse_scored: bool = False


class RiskScores(BaseModel):
    """All axis scores - dynamic dict for universal axes"""
    scores: dict[str, AxisScore] = {}

    def get_effective_scores(self) -> list[int]:
        """Get scores with reverse scoring applied (for tier calculation)"""
        effective = []
        for axis_id, axis_score in self.scores.items():
            if axis_score.reverse_scored:
                # Invert: 0->3, 1->2, 2->1, 3->0
                effective.append(3 - axis_score.score)
            else:
                effective.append(axis_score.score)
        return effective

    def max_effective_score(self) -> int:
        """Get the maximum effective score (after reverse scoring)"""
        scores = self.get_effective_scores()
        return max(scores) if scores else 0


class AxisInfo(BaseModel):
    """Axis info for display"""
    id: str
    name: str
    section: Optional[str] = None
    reverse_scored: bool = False


class Assessment(BaseModel):
    """Complete assessment record"""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    input: ResearchInput
    scores: RiskScores
    tier: Tier
    recommendations: list[str]
    axes_used: Optional[list[AxisInfo]] = None


class AssessmentsStore(BaseModel):
    """JSON file structure"""
    assessments: list[Assessment] = []


class URLFetchRequest(BaseModel):
    """Request to fetch and parse a URL"""
    url: str


class URLFetchResponse(BaseModel):
    """Parsed content from URL"""
    title: str
    abstract: str
    snippet: Optional[str] = None
    success: bool
    error: Optional[str] = None


class AssessRequest(BaseModel):
    """Request to assess a research paper"""
    title: str
    abstract: str
    snippet: Optional[str] = None
    source_url: Optional[str] = None
    dissemination: Dissemination
    audience: Audience
    # category is auto-detected by LLM, not required from user


class RiskAxis(BaseModel):
    """Definition of a risk axis"""
    id: str
    name: str
    question: str
    section: Optional[str] = None
    reverse_scored: bool = False


class UniversalAxesConfig(BaseModel):
    """Universal axes configuration file structure"""
    universal: bool = True
    axes: list[RiskAxis] = []
    sections: dict[str, str] = {}
    scoring_rubric: dict[str, str] = {}
    reverse_scoring_note: Optional[str] = None
