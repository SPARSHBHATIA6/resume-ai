"""Optional OpenAI-powered recommendations.

The application remains fully functional when OPENAI_API_KEY is absent.
"""

import os
from typing import Dict


def ai_available() -> bool:
    """Return whether an API key is configured."""
    return bool(os.getenv("OPENAI_API_KEY"))


def generate_ai_recommendations(resume_text: str, job_description: str, missing_skills: list[str]) -> Dict[str, str]:
    """Generate structured suggestions using OpenAI when configured.

    Imports are lazy so the basic mode does not require the OpenAI package.
    """
    if not ai_available():
        return {}
    try:
        from openai import OpenAI

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        prompt = f"""You are a resume coach. Analyze the resume against the job description.
Do not invent achievements, metrics, employers, education, or skills. Return concise JSON with keys:
summary, resume_improvements, project_improvements, job_specific_advice.
Resume:\n{resume_text[:12000]}\n\nJob description:\n{job_description[:10000]}\n\nMissing skills:\n{', '.join(missing_skills)}"""
        response = client.responses.create(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), input=prompt)
        text = response.output_text
        return {"ai_advice": text}
    except Exception as exc:
        return {"error": f"AI recommendations unavailable: {exc}"}
