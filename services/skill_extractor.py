"""Skill extraction and lightweight resume section parsing."""

import json
import re
from pathlib import Path
from typing import Dict, List

from utils.text_processing import contains_phrase, normalize_text

SKILLS_PATH = Path(__file__).resolve().parent.parent / "data" / "skills.json"


def load_skill_database() -> Dict[str, List[str]]:
    """Load skill categories from JSON so the list is easy to extend."""
    with SKILLS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def canonical_skill_map() -> Dict[str, str]:
    """Map aliases to a display-friendly canonical skill name."""
    mapping = {}
    for _, skills in load_skill_database().items():
        for skill in skills:
            canonical = skill
            aliases = {skill.lower()}
            if skill == "Natural Language Processing":
                aliases.add("nlp")
            if skill == "Scikit-learn":
                aliases.update({"sklearn", "scikit learn"})
            if skill == "REST APIs":
                aliases.update({"rest api", "restful api", "rest apis"})
            if skill == "Google Cloud":
                aliases.add("gcp")
            for alias in aliases:
                mapping[alias] = canonical
    return mapping


def extract_skills(text: str) -> List[str]:
    """Find known skills in text using case-insensitive word-aware matching."""
    lowered = (text or "").lower()
    found = set()
    for alias, canonical in canonical_skill_map().items():
        if contains_phrase(lowered, alias):
            found.add(canonical)
    return sorted(found, key=str.lower)


def extract_contact_info(text: str) -> Dict[str, str]:
    """Extract common contact details without inventing missing values."""
    normalized = normalize_text(text)
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", normalized)
    phone = re.search(r"(?:\+?\d[\d\s().-]{8,}\d)", normalized)
    linkedin = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+", normalized, re.I)
    github = re.search(r"(?:https?://)?(?:www\.)?github\.com/[\w-]+", normalized, re.I)
    return {
        "email": email.group(0) if email else "",
        "phone": phone.group(0).strip() if phone else "",
        "linkedin": linkedin.group(0) if linkedin else "",
        "github": github.group(0) if github else "",
    }


def extract_name(text: str) -> str:
    """Best-effort name extraction from the first few non-empty lines."""
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    for line in lines[:8]:
        if any(marker in line.lower() for marker in ["resume", "curriculum vitae", "cv"]):
            continue
        if "@" in line or "http" in line or re.search(r"\d", line):
            continue
        words = line.split()
        if 2 <= len(words) <= 5 and all(re.match(r"^[A-Za-z.'-]+$", word) for word in words):
            return line
    return "Not detected"


def extract_sections(text: str) -> Dict[str, str]:
    """Split a resume into common sections using heading detection."""
    headings = {
        "education": r"education|academic background|qualifications",
        "skills": r"skills|technical skills|technologies",
        "projects": r"projects|academic projects|personal projects",
        "experience": r"experience|work experience|internships|employment",
        "certifications": r"certifications|certificates|courses",
        "summary": r"summary|profile|objective|about me",
    }
    lines = (text or "").splitlines()
    sections = {key: "" for key in headings}
    current = "summary"
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        detected = None
        for key, pattern in headings.items():
            if re.fullmatch(r"(?:\s*[-:|]?\s*)?(?:" + pattern + r")(?:\s*[-:|]?\s*)?", stripped, re.I):
                detected = key
                break
        if detected:
            current = detected
        else:
            sections[current] += stripped + "\n"
    return {key: value.strip() for key, value in sections.items()}


def extract_resume_profile(text: str) -> Dict:
    """Return structured resume information for the dashboard."""
    sections = extract_sections(text)
    contacts = extract_contact_info(text)
    return {
        "name": extract_name(text),
        **contacts,
        "education": sections["education"],
        "skills_text": sections["skills"],
        "projects": sections["projects"],
        "experience": sections["experience"],
        "certifications": sections["certifications"],
        "summary": sections["summary"],
        "skills": extract_skills(text),
    }
