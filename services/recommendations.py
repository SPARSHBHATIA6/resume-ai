"""Rule-based recommendations that work without an AI API."""

from typing import Dict, List


def build_recommendations(profile: Dict, missing_skills: List[str], keyword_missing: List[str]) -> List[str]:
    """Create actionable suggestions without inventing candidate facts."""
    recommendations = []
    if not profile.get("summary"):
        recommendations.append("Add a concise professional summary tailored to the target role.")
    if missing_skills:
        recommendations.append("Add relevant missing skills only when you genuinely have experience with them; avoid keyword stuffing.")
    if profile.get("projects") and not any(char.isdigit() for char in profile["projects"]):
        recommendations.append("Where truthful, add measurable project outcomes such as latency, accuracy, users, scale, or time saved.")
    if not profile.get("github"):
        recommendations.append("Consider adding a GitHub link with your strongest relevant projects.")
    if not profile.get("certifications"):
        recommendations.append("Add relevant certifications or coursework when they strengthen your fit for the role.")
    if len(profile.get("experience", "")) < 60:
        recommendations.append("Strengthen experience bullets with action verbs, tools used, and concrete outcomes.")
    if keyword_missing:
        recommendations.append("Review missing job keywords and naturally incorporate the ones that genuinely describe your experience.")
    recommendations.append("Keep the resume concise and remove irrelevant details that do not support the target role.")
    return recommendations[:7]


def project_suggestions(project_text: str) -> List[str]:
    """Suggest stronger project-writing patterns without inventing metrics."""
    if not project_text.strip():
        return ["Add 2–4 projects with the problem, technologies, your contribution, and measurable impact where available."]
    return [
        "Describe each project using action + technology + outcome.",
        "Replace generic phrases like 'created a project' with the specific problem you solved.",
        "Add a real metric only if you measured it, such as accuracy, response time, users, or dataset size.",
    ]


def skills_to_learn(missing_skills: List[str]) -> List[Dict[str, str]]:
    """Rank missing skills by practical priority."""
    high_terms = {"Python", "SQL", "Machine Learning", "Git", "Pandas", "NumPy", "REST API", "REST APIs", "Scikit-learn"}
    results = []
    for skill in missing_skills:
        priority = "High" if skill in high_terms else "Medium"
        reason = "Frequently useful for core development and data/ML workflows." if priority == "High" else "Can strengthen your fit for related roles and broaden your technical toolkit."
        results.append({"skill": skill, "priority": priority, "reason": reason})
    return results[:8]
