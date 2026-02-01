"""Dashboard analytics API endpoints"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.services.storage import get_all_assessments

router = APIRouter()


def assessment_to_dict(a) -> dict:
    """Convert Assessment Pydantic model to dict for easier processing"""
    return a.model_dump(mode="json")


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tier: Optional[str] = Query(None, description="Filter by risk tier"),
    dissemination: Optional[str] = Query(None, description="Filter by dissemination"),
    audience: Optional[str] = Query(None, description="Filter by audience")
):
    """Get dashboard statistics with optional filters"""

    assessments = get_all_assessments()

    # Convert to dicts for easier processing
    all_assessments = [assessment_to_dict(a) for a in assessments]

    # Apply filters
    filtered = []
    for a in all_assessments:
        # Date filter
        if date_from:
            try:
                from_date = datetime.fromisoformat(date_from)
                ts = a.get("timestamp", "")
                if isinstance(ts, str):
                    ts = ts.replace("Z", "")
                    if datetime.fromisoformat(ts) < from_date:
                        continue
            except:
                pass

        if date_to:
            try:
                to_date = datetime.fromisoformat(date_to) + timedelta(days=1)
                ts = a.get("timestamp", "")
                if isinstance(ts, str):
                    ts = ts.replace("Z", "")
                    if datetime.fromisoformat(ts) >= to_date:
                        continue
            except:
                pass

        # Category filter
        if category and category != "all":
            paper_category = a.get("input", {}).get("category")
            if paper_category != category:
                continue

        # Tier filter
        if tier and tier != "all":
            if a.get("tier") != tier:
                continue

        # Dissemination filter
        if dissemination and dissemination != "all":
            if a.get("input", {}).get("dissemination") != dissemination:
                continue

        # Audience filter
        if audience and audience != "all":
            if a.get("input", {}).get("audience") != audience:
                continue

        filtered.append(a)

    # Calculate statistics
    total = len(filtered)

    # Risk distribution
    risk_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for a in filtered:
        tier_val = a.get("tier", "Low")
        if tier_val in risk_counts:
            risk_counts[tier_val] += 1

    # High + Critical percentage
    high_critical = risk_counts["High"] + risk_counts["Critical"]
    high_critical_pct = round((high_critical / total * 100), 1) if total > 0 else 0

    # Category distribution
    category_counts = defaultdict(int)
    for a in filtered:
        cat = a.get("input", {}).get("category", "unknown")
        if cat:
            category_counts[cat] += 1
        else:
            category_counts["unknown"] += 1

    # Top categories
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    top_categories = sorted_categories[:3]

    # High-risk category (most high+critical papers)
    high_risk_by_category = defaultdict(int)
    for a in filtered:
        if a.get("tier") in ["High", "Critical"]:
            cat = a.get("input", {}).get("category", "unknown")
            high_risk_by_category[cat] += 1

    top_high_risk_category = max(high_risk_by_category.items(), key=lambda x: x[1])[0] if high_risk_by_category else None

    # Axis-level statistics
    axis_totals = defaultdict(lambda: {"sum": 0, "count": 0})
    for a in filtered:
        scores = a.get("scores", {})
        if "scores" in scores:
            scores = scores["scores"]

        for axis_id, axis_data in scores.items():
            if isinstance(axis_data, dict) and "score" in axis_data:
                score = axis_data["score"]
                # For reverse-scored axes, invert for analysis
                if axis_data.get("reverse_scored", False):
                    score = 3 - score
                axis_totals[axis_id]["sum"] += score
                axis_totals[axis_id]["count"] += 1

    # Calculate averages per axis
    axis_averages = {}
    for axis_id, data in axis_totals.items():
        if data["count"] > 0:
            axis_averages[axis_id] = round(data["sum"] / data["count"], 2)

    # Most stressed axis
    most_stressed_axis = max(axis_averages.items(), key=lambda x: x[1]) if axis_averages else (None, 0)

    # Capability/Impact index (A1, A2, D1, D2)
    capability_axes = ["A1", "A2", "D1", "D2"]
    capability_scores = [axis_averages.get(a, 0) for a in capability_axes if a in axis_averages]
    capability_index = round(sum(capability_scores) / len(capability_scores), 2) if capability_scores else 0

    # Safeguard/Governance index (C1, C2, F1, F2)
    safeguard_axes = ["C1", "C2", "F1", "F2"]
    safeguard_scores = [axis_averages.get(a, 0) for a in safeguard_axes if a in axis_averages]
    safeguard_index = round(sum(safeguard_scores) / len(safeguard_scores), 2) if safeguard_scores else 0

    # Gap indicator
    governance_gap = round(capability_index - safeguard_index, 2)

    # Section averages
    section_averages = {}
    sections = {
        "A": ["A1", "A2"],
        "B": ["B1", "B2"],
        "C": ["C1", "C2"],
        "D": ["D1", "D2"],
        "E": ["E1", "E2"],
        "F": ["F1", "F2"]
    }
    for section, axes in sections.items():
        scores = [axis_averages.get(a, 0) for a in axes if a in axis_averages]
        section_averages[section] = round(sum(scores) / len(scores), 2) if scores else 0

    # Recent high-risk paper
    high_risk_papers = [a for a in filtered if a.get("tier") in ["High", "Critical"]]
    high_risk_papers.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    recent_high_risk = None
    if high_risk_papers:
        p = high_risk_papers[0]
        recent_high_risk = {
            "id": p.get("id"),
            "title": p.get("input", {}).get("title", "Untitled"),
            "tier": p.get("tier"),
            "category": p.get("input", {}).get("category"),
            "timestamp": p.get("timestamp")
        }

    # Trend data (assessments per day for last 30 days)
    trend_data = defaultdict(lambda: {"total": 0, "high_critical": 0})
    for a in filtered:
        try:
            date_str = str(a.get("timestamp", ""))[:10]
            trend_data[date_str]["total"] += 1
            if a.get("tier") in ["High", "Critical"]:
                trend_data[date_str]["high_critical"] += 1
        except:
            pass

    # Sort trend data
    trend_sorted = sorted(trend_data.items(), key=lambda x: x[0])[-30:]

    return {
        "total_assessed": total,
        "risk_distribution": risk_counts,
        "high_critical_count": high_critical,
        "high_critical_percentage": high_critical_pct,
        "category_distribution": dict(category_counts),
        "top_categories": top_categories,
        "top_high_risk_category": top_high_risk_category,
        "axis_averages": axis_averages,
        "section_averages": section_averages,
        "most_stressed_axis": {
            "axis": most_stressed_axis[0],
            "average": most_stressed_axis[1]
        },
        "capability_index": capability_index,
        "safeguard_index": safeguard_index,
        "governance_gap": governance_gap,
        "recent_high_risk": recent_high_risk,
        "trend_data": [{"date": d, **v} for d, v in trend_sorted],
        "filtered_count": total
    }


@router.get("/dashboard/assessments")
async def get_filtered_assessments(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    tier: Optional[str] = Query(None),
    dissemination: Optional[str] = Query(None),
    audience: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get filtered assessment list for dashboard"""

    assessments = get_all_assessments()

    # Convert to dicts
    all_assessments = [assessment_to_dict(a) for a in assessments]

    # Apply same filters as stats
    filtered = []
    for a in all_assessments:
        if date_from:
            try:
                from_date = datetime.fromisoformat(date_from)
                ts = a.get("timestamp", "")
                if isinstance(ts, str):
                    ts = ts.replace("Z", "")
                    if datetime.fromisoformat(ts) < from_date:
                        continue
            except:
                pass

        if date_to:
            try:
                to_date = datetime.fromisoformat(date_to) + timedelta(days=1)
                ts = a.get("timestamp", "")
                if isinstance(ts, str):
                    ts = ts.replace("Z", "")
                    if datetime.fromisoformat(ts) >= to_date:
                        continue
            except:
                pass

        if category and category != "all":
            if a.get("input", {}).get("category") != category:
                continue

        if tier and tier != "all":
            if a.get("tier") != tier:
                continue

        if dissemination and dissemination != "all":
            if a.get("input", {}).get("dissemination") != dissemination:
                continue

        if audience and audience != "all":
            if a.get("input", {}).get("audience") != audience:
                continue

        filtered.append(a)

    # Sort by timestamp descending
    filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    # Paginate
    total = len(filtered)
    paginated = filtered[offset:offset + limit]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "assessments": paginated
    }
