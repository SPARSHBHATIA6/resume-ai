"""ResumeAI — AI-powered resume analyzer.

Run with:
    streamlit run app.py
"""

import html
import os
from pathlib import Path
from typing import Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from database.db import delete_history, init_db, list_analyses, save_analysis
from models.scoring import WEIGHTS, ats_compatibility, calculate_scores
from reports.pdf_report import generate_report
from services.ai_service import ai_available, generate_ai_recommendations
from services.job_analyzer import compare_skills, extract_job_requirements, keyword_match, tfidf_similarity
from services.pdf_parser import extract_text_from_pdf
from services.recommendations import build_recommendations, project_suggestions, skills_to_learn
from services.skill_extractor import extract_resume_profile
from utils.validators import validate_job_description, validate_pdf, validate_resume_text

load_dotenv()
init_db()

st.set_page_config(page_title="ResumeAI — Resume Analyzer", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

LIGHT_CSS = """
<style>
:root { --bg:#f6f8fc; --card:#ffffff; --text:#111827; --muted:#64748b; --border:#e5e7eb; --accent:#6d5dfc; --accent2:#3b82f6; }
.stApp { background:var(--bg); color:var(--text); }
.block-container { max-width:1250px; padding-top:2rem; padding-bottom:3rem; }
[data-testid="stSidebar"] { background:#0f172a; }
[data-testid="stSidebar"] * { color:#e2e8f0 !important; }
.hero { background:linear-gradient(135deg,#111827 0%,#312e81 60%,#2563eb 100%); color:white; border-radius:28px; padding:48px; margin-bottom:28px; box-shadow:0 18px 55px rgba(30,41,59,.16); }
.hero h1 { font-size:clamp(2.2rem,5vw,4.4rem); line-height:1.02; margin:0 0 18px; letter-spacing:-.055em; }
.hero p { color:#dbeafe; font-size:1.1rem; max-width:650px; line-height:1.7; }
.eyebrow { text-transform:uppercase; letter-spacing:.16em; font-size:.76rem; font-weight:800; color:#c4b5fd; margin-bottom:12px; }
.card { background:var(--card); border:1px solid var(--border); border-radius:20px; padding:22px; box-shadow:0 8px 30px rgba(15,23,42,.05); margin-bottom:16px; }
.metric-card { min-height:135px; display:flex; flex-direction:column; justify-content:space-between; }
.metric-label { color:var(--muted); font-size:.88rem; font-weight:700; }
.metric-value { font-size:2rem; font-weight:850; letter-spacing:-.04em; }
.muted { color:var(--muted); }
.section-title { font-size:1.45rem; font-weight:850; letter-spacing:-.03em; margin:22px 0 12px; }
.chip { display:inline-block; background:#eef2ff; color:#4338ca; border:1px solid #ddd6fe; padding:6px 10px; border-radius:999px; margin:3px 4px 3px 0; font-size:.8rem; font-weight:750; }
.chip.green { background:#ecfdf5; color:#047857; border-color:#a7f3d0; }
.chip.red { background:#fff1f2; color:#be123c; border-color:#fecdd3; }
.chip.gray { background:#f1f5f9; color:#475569; border-color:#e2e8f0; }
.notice { background:#eff6ff; border:1px solid #bfdbfe; color:#1e40af; padding:13px 16px; border-radius:14px; margin:10px 0 16px; }
.privacy { background:#fff; border:1px solid #e2e8f0; padding:12px 15px; border-radius:13px; color:#475569; font-size:.82rem; }
.small { font-size:.82rem; color:var(--muted); }
.feature { height:100%; }
.feature h3 { margin-bottom:6px; }
.progress-shell { height:10px; background:#e2e8f0; border-radius:99px; overflow:hidden; }
.progress-bar { height:100%; background:linear-gradient(90deg,#6d5dfc,#3b82f6); border-radius:99px; }
.demo-preview { background:linear-gradient(180deg,#fff,#f8fafc); border:1px solid #e2e8f0; border-radius:20px; padding:20px; box-shadow:0 18px 50px rgba(15,23,42,.12); }
.demo-line { height:10px; background:#e2e8f0; border-radius:99px; margin:10px 0; }
[data-testid="stFileUploaderDropzone"] { border:1.5px dashed #a5b4fc; background:#f8faff; border-radius:18px; }
button[kind="primary"] { border-radius:12px; font-weight:800; }
</style>
"""

DARK_CSS = """
<style>
:root { --bg:#070b14; --card:#101827; --text:#f8fafc; --muted:#94a3b8; --border:#243244; }
.stApp { background:var(--bg); color:var(--text); }
[data-testid="stSidebar"] { background:#030712; }
.card,.demo-preview { background:#101827; border-color:#243244; }
.notice { background:#0c1d36; border-color:#1d4ed8; color:#bfdbfe; }
.privacy { background:#101827; border-color:#243244; color:#cbd5e1; }
.chip { background:#1e1b4b; color:#c4b5fd; border-color:#4c1d95; }
.chip.green { background:#052e24; color:#6ee7b7; border-color:#065f46; }
.chip.red { background:#3b0a18; color:#fda4af; border-color:#881337; }
.chip.gray { background:#172033; color:#cbd5e1; border-color:#334155; }
.progress-shell { background:#243244; }
.demo-line { background:#243244; }
[data-testid="stFileUploaderDropzone"] { background:#0f172a; border-color:#4f46e5; }
</style>
"""

SAMPLE_RESUME = """Aarav Mehta
Email: aarav.mehta@example.com | +91 9876543210
LinkedIn: linkedin.com/in/aaravmehta | GitHub: github.com/aaravmehta

SUMMARY
B.Tech Computer Science student focused on Python, machine learning and data-driven applications.

EDUCATION
B.Tech in Computer Science and Engineering, 2027

SKILLS
Python, C++, SQL, Pandas, NumPy, Scikit-learn, Machine Learning, Git, GitHub, Flask, HTML, CSS

PROJECTS
Resume Classifier — Built a machine learning classifier with Python and Scikit-learn to categorize resumes.
Campus Event Portal — Developed a Flask web application with SQL for event registration and management.

EXPERIENCE
Software Engineering Intern — Built Python utilities, worked with Git and improved data processing workflows.

CERTIFICATIONS
Python for Data Science
"""

SAMPLE_JOB = """We are looking for a Python Developer / ML Intern with strong Python, SQL, Git, Pandas, NumPy, Machine Learning and REST API knowledge. Experience with Scikit-learn, Docker, AWS and FastAPI is preferred. Candidates should understand data processing, build maintainable applications, work with a team, and communicate technical ideas clearly. A Computer Science or related degree is preferred."""


def init_state() -> None:
    defaults = {"page": "Home", "theme": "Light", "resume_text": "", "resume_name": "", "job_description": "", "analysis": None, "uploaded_profile": None}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def chips(items: List[str], kind: str = "") -> str:
    if not items:
        return '<span class="small">None detected</span>'
    safe = []
    for item in items:
        safe.append(f'<span class="chip {kind}">{html.escape(str(item))}</span>')
    return "".join(safe)


def metric_card(value: str, label: str, sub: str = "") -> None:
    st.markdown(f'<div class="card metric-card"><div class="metric-label">{html.escape(label)}</div><div class="metric-value">{html.escape(value)}</div><div class="small">{html.escape(sub)}</div></div>', unsafe_allow_html=True)


def render_sidebar() -> None:
    st.sidebar.markdown("# ◈ ResumeAI")
    st.sidebar.caption("AI-powered resume intelligence")
    for page in ["Home", "Analyze", "Dashboard", "History"]:
        if st.sidebar.button(page, use_container_width=True, type="primary" if st.session_state.page == page else "secondary"):
            st.session_state.page = page
            st.rerun()
    st.sidebar.divider()
    st.sidebar.markdown("### Appearance")
    dark = st.sidebar.toggle("Dark mode", value=st.session_state.theme == "Dark")
    st.session_state.theme = "Dark" if dark else "Light"
    st.sidebar.markdown('<div class="privacy">🔒 Your resume is processed for analysis. Do not upload resumes containing information you are not comfortable processing.<br><br>ResumeAI does not permanently store uploaded PDF files.</div>', unsafe_allow_html=True)
    if ai_available():
        st.sidebar.success("Advanced AI mode enabled")
    else:
        st.sidebar.info("Basic NLP mode · no API key needed")


def render_home() -> None:
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">AI Resume Intelligence</div>
      <h1>Analyze your resume.<br>Understand your chances.</h1>
      <p>Compare your resume with any job description and discover exactly what you should improve — with transparent scoring, ATS-style keyword analysis and practical skill-gap recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns([1.05, .95], gap="large")
    with c1:
        if st.button("Analyze My Resume →", type="primary", use_container_width=True):
            st.session_state.page = "Analyze"
            st.rerun()
        if st.button("Try Demo", use_container_width=True):
            st.session_state.resume_text = SAMPLE_RESUME
            st.session_state.resume_name = "demo_resume.txt"
            st.session_state.job_description = SAMPLE_JOB
            st.session_state.uploaded_profile = extract_resume_profile(SAMPLE_RESUME)
            run_analysis(SAMPLE_RESUME, SAMPLE_JOB, "demo_resume.txt")
            st.session_state.page = "Dashboard"
            st.rerun()
    with c2:
        st.markdown("""
        <div class="demo-preview">
          <div class="small">LIVE ANALYSIS PREVIEW</div>
          <h3 style="margin:7px 0 18px">Your Resume Match</h3>
          <div style="display:flex;align-items:center;gap:18px">
            <div style="font-size:42px;font-weight:850">87%</div>
            <div style="flex:1"><div class="progress-shell"><div class="progress-bar" style="width:87%"></div></div><div class="small" style="margin-top:8px">Strong match for Python / ML roles</div></div>
          </div>
          <div class="demo-line" style="width:90%"></div><div class="demo-line" style="width:72%"></div><div class="demo-line" style="width:82%"></div>
          <div style="margin-top:18px"><span class="chip green">Python</span><span class="chip green">SQL</span><span class="chip green">Pandas</span><span class="chip red">Docker</span></div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="section-title">Everything you need to improve a targeted resume</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    features = [("AI Resume Analysis", "Extract structured resume information and actionable insights."), ("ATS Keyword Check", "Find important job terms your resume does and does not cover."), ("Skill Gap Detection", "Separate matched skills from high-value missing skills."), ("Job Match Score", "Understand a transparent, configurable portfolio-style score.")]
    for col, (title, body) in zip(cols, features):
        with col:
            st.markdown(f'<div class="card feature"><h3>{title}</h3><div class="muted">{body}</div></div>', unsafe_allow_html=True)


def render_analyze() -> None:
    st.markdown('<div class="section-title">Analyze a resume</div>', unsafe_allow_html=True)
    st.caption("Upload a text-based PDF and paste the target job description. ResumeAI runs locally in basic mode.")
    left, right = st.columns([.95, 1.05], gap="large")
    with left:
        st.markdown('<div class="card"><h3>1. Upload resume</h3><div class="muted">PDF only · max 5 MB</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Drop your resume here", type=["pdf"], label_visibility="collapsed")
        if uploaded:
            ok, error = validate_pdf(uploaded)
            if not ok:
                st.error(error)
            else:
                try:
                    text = extract_text_from_pdf(uploaded)
                    valid, error = validate_resume_text(text)
                    if not valid:
                        st.error(error)
                    else:
                        st.session_state.resume_text = text
                        st.session_state.resume_name = uploaded.name
                        st.session_state.uploaded_profile = extract_resume_profile(text)
                        st.success(f"Uploaded {uploaded.name} · {uploaded.size / 1024:.1f} KB")
                except Exception:
                    st.error("This PDF could not be read. Please try another valid text-based PDF.")
        elif st.session_state.resume_text:
            st.info(f"Using {st.session_state.resume_name}. Upload another PDF to replace it.")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.session_state.uploaded_profile:
            profile = st.session_state.uploaded_profile
            st.markdown('<div class="card"><h3>Extracted profile</h3>', unsafe_allow_html=True)
            st.write(f"**Name:** {profile['name']}")
            st.write(f"**Email:** {profile['email'] or 'Not detected'}")
            st.write(f"**Phone:** {profile['phone'] or 'Not detected'}")
            st.write(f"**LinkedIn:** {profile['linkedin'] or 'Not detected'}")
            st.write(f"**GitHub:** {profile['github'] or 'Not detected'}")
            st.markdown("**Detected skills**")
            st.markdown(chips(profile["skills"]), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card"><h3>2. Add job description</h3><div class="muted">Paste the job you want to target</div>', unsafe_allow_html=True)
        job = st.text_area("Job description", value=st.session_state.job_description, height=330, placeholder="Example: Looking for a Python Developer with Python, SQL, Git, Pandas, NumPy, Machine Learning and REST APIs...", label_visibility="collapsed")
        st.caption(f"{len(job):,} characters")
        a, b = st.columns(2)
        with a:
            if st.button("Load sample job", use_container_width=True):
                st.session_state.job_description = SAMPLE_JOB
                st.rerun()
        with b:
            if st.button("Clear", use_container_width=True):
                st.session_state.job_description = ""
                st.rerun()
        st.session_state.job_description = job
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="notice">💡 ResumeAI estimates match quality using skills, keywords, section completeness and project relevance. It is not the exact score used by any company ATS.</div>', unsafe_allow_html=True)
        if st.button("Analyze Resume →", type="primary", use_container_width=True):
            run_with_progress(job)


def run_with_progress(job: str) -> None:
    resume = st.session_state.resume_text
    ok, error = validate_resume_text(resume)
    if not ok:
        st.error(error)
        return
    ok, error = validate_job_description(job)
    if not ok:
        st.error(error)
        return
    steps = ["Reading resume", "Extracting information", "Identifying skills", "Analyzing job description", "Comparing requirements", "Generating recommendations"]
    progress = st.progress(0)
    status = st.empty()
    for index, step in enumerate(steps, start=1):
        status.info(f"{step}…")
        # Each step is deliberately lightweight; the progress UI communicates the pipeline without freezing the app.
        if index == len(steps):
            run_analysis(resume, job, st.session_state.resume_name)
        progress.progress(index / len(steps))
    status.success("Analysis complete.")
    st.session_state.page = "Dashboard"
    st.rerun()


def run_analysis(resume_text: str, job_description: str, resume_name: str) -> None:
    profile = extract_resume_profile(resume_text)
    job_info = extract_job_requirements(job_description)
    comparison = compare_skills(profile["skills"], job_info["skills"], job_description)
    skill_pct = (len(comparison["matched"]) / len(job_info["skills"]) * 100) if job_info["skills"] else 0
    keywords = keyword_match(resume_text, job_info["keywords"])
    keyword_pct = (len(keywords["found"]) / keywords["total"] * 100) if keywords["total"] else 0
    scores = calculate_scores(skill_pct, keyword_pct, profile["experience"], profile["education"], profile["projects"])
    ats = ats_compatibility(keyword_pct, resume_text)
    recommendations = build_recommendations(profile, comparison["missing"], keywords["missing"])
    learned = skills_to_learn(comparison["missing"])
    result = {
        "resume_name": resume_name,
        "profile": profile,
        "job_description": job_description,
        "job_skills": job_info["skills"],
        "matched_skills": comparison["matched"],
        "missing_skills": comparison["missing"],
        "optional_skills": comparison.get("optional", []),
        "keyword_analysis": keywords,
        "scores": scores,
        "ats": ats,
        "tfidf": tfidf_similarity(resume_text, job_description),
        "recommendations": recommendations,
        "project_suggestions": project_suggestions(profile["projects"]),
        "skills_to_learn": learned,
    }
    ai_result = generate_ai_recommendations(resume_text, job_description, comparison["missing"])
    result["ai"] = ai_result
    result["analysis_id"] = save_analysis(resume_name, scores["overall"], comparison["matched"], comparison["missing"])
    st.session_state.analysis = result


def render_dashboard() -> None:
    result = st.session_state.analysis
    if not result:
        st.info("No analysis yet. Start with Analyze or Try Demo.")
        if st.button("Go to Analyze", type="primary"):
            st.session_state.page = "Analyze"
            st.rerun()
        return
    score = result["scores"]["overall"]
    st.markdown(f'<div class="hero" style="padding:30px 36px"><div class="eyebrow">Resume Analysis</div><h1 style="font-size:2.6rem">{html.escape(result["profile"]["name"])} · {score}% match</h1><p>Targeted analysis for {html.escape(result["resume_name"])}. Use the sections below to understand your strengths and gaps.</p></div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1: metric_card(f"{score:.0f}%", "Match Score", "Estimated overall fit")
    with m2: metric_card(f"{len(result['matched_skills'])}/{len(result['job_skills'])}", "Skills Matched", "Against detected job skills")
    with m3: metric_card(str(len(result["missing_skills"])), "Missing Skills", "Skills worth reviewing")
    with m4: metric_card(f"{result['ats']:.0f}%", "ATS Compatibility", "Estimated keyword readiness")

    tabs = st.tabs(["Overview", "Skills", "ATS Analysis", "Job Match", "Projects", "Recommendations", "Resume Details"])
    with tabs[0]: render_overview(result)
    with tabs[1]: render_skills(result)
    with tabs[2]: render_ats(result)
    with tabs[3]: render_job_match(result)
    with tabs[4]: render_projects(result)
    with tabs[5]: render_recommendations(result)
    with tabs[6]: render_resume_details(result)

    report = generate_report(result)
    st.download_button("Download Analysis Report", data=report, file_name="resumeai-analysis-report.pdf", mime="application/pdf", type="primary")


def render_overview(result: Dict) -> None:
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        st.markdown('<div class="card"><h3>Score breakdown</h3>', unsafe_allow_html=True)
        labels = ["Skills", "Keywords", "Experience", "Education", "Projects"]
        values = [result["scores"][x] for x in ["skills", "keywords", "experience", "education", "projects"]]
        fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", text=[f"{v:.0f}%" for v in values], textposition="auto"))
        fig.update_layout(height=320, margin=dict(l=10,r=10,t=10,b=10), xaxis=dict(range=[0,100]), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("<div class='small'>Weighted methodology: 50% skills · 20% keywords · 15% experience · 10% education · 5% projects.</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><h3>Skill coverage</h3>', unsafe_allow_html=True)
        matched = len(result["matched_skills"]); missing = len(result["missing_skills"])
        fig = go.Figure(data=[go.Pie(labels=["Matched", "Missing"], values=[matched, missing], hole=.68, textinfo="label+percent")])
        fig.update_layout(height=320, margin=dict(l=10,r=10,t=10,b=10), showlegend=True, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown(f"**TF-IDF similarity:** {result['tfidf']:.1f}% — useful as an additional semantic signal, not a final hiring judgment.")
        st.markdown('</div>', unsafe_allow_html=True)


def render_skills(result: Dict) -> None:
    a, b = st.columns(2)
    with a:
        st.markdown('<div class="card"><h3>Matched skills</h3>', unsafe_allow_html=True)
        st.markdown(chips(result["matched_skills"], "green"), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="card"><h3>Missing skills</h3>', unsafe_allow_html=True)
        st.markdown(chips(result["missing_skills"], "red"), unsafe_allow_html=True)
        if result.get("optional_skills"):
            st.markdown("**Optional / preferred**")
            st.markdown(chips(result["optional_skills"], "gray"), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><h3>Detected resume skills</h3>', unsafe_allow_html=True)
    st.markdown(chips(result["profile"]["skills"]), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_ats(result: Dict) -> None:
    ka = result["keyword_analysis"]
    st.markdown('<div class="card"><h3>ATS-style keyword analysis</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: metric_card(str(ka["total"]), "Important Keywords")
    with c2: metric_card(str(len(ka["found"])), "Keywords Found")
    with c3: metric_card(str(len(ka["missing"])), "Keywords Missing")
    st.markdown("**Found**")
    st.markdown(chips(ka["found"], "green"), unsafe_allow_html=True)
    st.markdown("**Missing**")
    st.markdown(chips(ka["missing"], "red"), unsafe_allow_html=True)
    st.warning("Add relevant keywords only if they genuinely describe your experience. Do not keyword-stuff your resume.")
    st.markdown('</div>', unsafe_allow_html=True)


def render_job_match(result: Dict) -> None:
    st.markdown('<div class="card"><h3>Job match methodology</h3><p class="muted">The score is a transparent estimate designed for learning and portfolio use, not a real company ATS score.</p>', unsafe_allow_html=True)
    for key, label in [("skills","Skills Match"),("keywords","Keyword Match"),("experience","Experience"),("education","Education"),("projects","Project Relevance")]:
        value = result["scores"][key]
        st.markdown(f"**{label} · {value:.0f}%**")
        st.progress(int(value))
    st.markdown('</div>', unsafe_allow_html=True)


def render_projects(result: Dict) -> None:
    st.markdown('<div class="card"><h3>Project analysis</h3>', unsafe_allow_html=True)
    if result["profile"]["projects"]:
        st.write(result["profile"]["projects"])
    else:
        st.info("No clear Projects section was detected. Consider adding relevant projects.")
    st.markdown("**How to improve project descriptions**")
    for item in result["project_suggestions"]:
        st.write(f"• {item}")
    st.markdown('<div class="notice"><b>Example pattern:</b> “Developed a machine learning model using Scikit-learn to predict student performance with 89% validation accuracy.” Only use metrics you actually measured.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_recommendations(result: Dict) -> None:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><h3>Resume improvements</h3>', unsafe_allow_html=True)
        for item in result["recommendations"]:
            st.write(f"• {item}")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><h3>Recommended skills to learn</h3>', unsafe_allow_html=True)
        for item in result["skills_to_learn"]:
            badge = "🔴" if item["priority"] == "High" else "🟡"
            st.write(f"{badge} **{item['skill']}** — {item['priority']} priority")
            st.caption(item["reason"])
        st.markdown('</div>', unsafe_allow_html=True)
    ai = result.get("ai", {})
    if ai.get("ai_advice"):
        st.markdown('<div class="card"><h3>Advanced AI recommendations</h3>', unsafe_allow_html=True)
        st.write(ai["ai_advice"])
        st.markdown('</div>', unsafe_allow_html=True)
    elif ai.get("error"):
        st.warning(ai["error"])


def render_resume_details(result: Dict) -> None:
    profile = result["profile"]
    cols = st.columns(2)
    fields = [("Name", profile["name"]), ("Email", profile["email"]), ("Phone", profile["phone"]), ("LinkedIn", profile["linkedin"]), ("GitHub", profile["github"]), ("Certifications", profile["certifications"])]
    for col, (label, value) in zip(cols * 3, fields):
        with col:
            st.markdown(f'<div class="card"><div class="small">{label}</div><div style="margin-top:7px">{html.escape(value or "Not detected")}</div></div>', unsafe_allow_html=True)
    with st.expander("View extracted resume text"):
        st.text_area("Extracted text", st.session_state.resume_text, height=300, label_visibility="collapsed")


def render_history() -> None:
    st.markdown('<div class="section-title">Analysis history</div>', unsafe_allow_html=True)
    st.caption("Only metadata is stored in SQLite — not the uploaded resume PDF.")
    history = list_analyses()
    if history:
        frame = pd.DataFrame(history)
        frame = frame[["id", "created_at", "resume_name", "match_score"]]
        frame.columns = ["ID", "Date", "Resume", "Match Score"]
        st.dataframe(frame, use_container_width=True, hide_index=True)
    else:
        st.info("No saved analyses yet. Run an analysis to create history.")
    if st.button("Delete Analysis History", type="secondary"):
        delete_history()
        st.success("Analysis history deleted.")
        st.rerun()


def main() -> None:
    init_state()
    st.markdown(DARK_CSS if st.session_state.theme == "Dark" else LIGHT_CSS, unsafe_allow_html=True)
    render_sidebar()
    page = st.session_state.page
    if page == "Home": render_home()
    elif page == "Analyze": render_analyze()
    elif page == "Dashboard": render_dashboard()
    else: render_history()


if __name__ == "__main__":
    main()
