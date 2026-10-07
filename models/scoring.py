"""Transparent resume scoring model."""

from typing import Dict, List

WEIGHTS = {
    "skills": 0.50,
    "keywords": 0.20,
    "experience": 0.15,
    "education": 0.10,
    "projects": 0.05,
}


def _presence_score(text: str, threshold: int = 40) -> float:
    """Simple completeness heuristic; deliberately not an ATS claim."""
    if not text.strip():
        return 0.0
    return min(100.0, max(35.0, len(text.strip()) / threshold * 100.0))


def calculate_scores(
    skill_match_pct: float,
    keyword_match_pct: float,
    experience_text: str,
    education_text: str,
    projects_text: str,
) -> Dict[str, float]:
    """Calculate weighted component and overall scores."""
    components = {
        "skills": round(skill_match_pct, 1),
        "keywords": round(keyword_match_pct, 1),
        "experience": round(_presence_score(experience_text), 1),
        "education": round(_presence_score(education_text), 1),
        "projects": round(_presence_score(projects_text), 1),
    }
    overall = round(sum(components[key] * WEIGHTS[key] for key in WEIGHTS), 1)
    return {**components, "overall": overall}


def ats_compatibility(keyword_pct: float, resume_text: str) -> float:
    """Estimate ATS readiness from keyword coverage and resume readability signals."""
    readability_bonus = 5 if len(resume_text.split()) >= 180 else 0
    return round(min(100.0, keyword_pct * 0.9 + readability_bonus), 1)
