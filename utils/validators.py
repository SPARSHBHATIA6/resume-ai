"""Input validation helpers."""

from typing import Tuple

MAX_FILE_SIZE_MB = 5
MIN_RESUME_CHARS = 150
MIN_JOB_CHARS = 80


def validate_pdf(uploaded_file) -> Tuple[bool, str]:
    """Validate an uploaded Streamlit file before parsing."""
    if uploaded_file is None:
        return False, "Please upload a PDF resume before starting the analysis."
    name = getattr(uploaded_file, "name", "")
    if not name.lower().endswith(".pdf"):
        return False, "Unsupported file. Please upload a PDF resume."
    size = getattr(uploaded_file, "size", 0)
    if size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f"The PDF is too large. Maximum allowed size is {MAX_FILE_SIZE_MB} MB."
    return True, ""


def validate_resume_text(text: str) -> Tuple[bool, str]:
    """Check that the extracted resume contains enough readable text."""
    if not text or not text.strip():
        return False, "Could not extract readable text from this PDF. Please upload a text-based PDF."
    if len(text.strip()) < MIN_RESUME_CHARS:
        return False, "This resume contains very little readable text. Please upload a clearer or more complete resume."
    return True, ""


def validate_job_description(text: str) -> Tuple[bool, str]:
    """Check job description length."""
    if not text or not text.strip():
        return False, "Please paste a job description before starting the analysis."
    if len(text.strip()) < MIN_JOB_CHARS:
        return False, f"The job description is too short. Please provide at least {MIN_JOB_CHARS} characters."
    return True, ""
