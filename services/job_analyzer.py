"""Job description analysis and keyword matching."""

from typing import Dict, List, Set
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from services.skill_extractor import extract_skills
from utils.text_processing import top_keywords


def extract_job_requirements(job_description: str) -> Dict:
    """Extract skills and important general keywords from a job description."""
    return {
        "skills": extract_skills(job_description),
        "keywords": top_keywords(job_description, 25),
    }


def compare_skills(resume_skills: List[str], job_skills: List[str], job_description: str = "") -> Dict[str, List[str]]:
    """Compare skill sets and classify preferred-only gaps as optional when detectable."""
    resume = {skill.lower(): skill for skill in resume_skills}
    matched = [resume[skill.lower()] for skill in job_skills if skill.lower() in resume]
    missing = [skill for skill in job_skills if skill.lower() not in resume]
    optional_context = " ".join(
        sentence for sentence in re.split(r"[.!?]", job_description or "")
        if re.search(r"\b(preferred|nice to have|bonus|plus)\b", sentence, re.I)
    )
    optional = [skill for skill in missing if re.search(r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)", optional_context.lower())]
    required_missing = [skill for skill in missing if skill not in optional]
    return {
        "matched": sorted(set(matched), key=str.lower),
        "missing": sorted(set(required_missing), key=str.lower),
        "optional": sorted(set(optional), key=str.lower),
    }


def keyword_match(resume_text: str, keywords: List[str]) -> Dict:
    """Measure important job-description keyword coverage."""
    lowered = (resume_text or "").lower()
    found = [keyword for keyword in keywords if keyword.lower() in lowered]
    missing = [keyword for keyword in keywords if keyword.lower() not in lowered]
    return {"total": len(keywords), "found": found, "missing": missing}


def tfidf_similarity(resume_text: str, job_description: str) -> float:
    """Compute a normalized 0-100 TF-IDF cosine similarity score."""
    if not resume_text.strip() or not job_description.strip():
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([resume_text, job_description])
    score = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    return round(score * 100, 1)
