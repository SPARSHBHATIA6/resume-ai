"""Professional PDF analysis report generator."""

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


def generate_report(result: dict) -> bytes:
    """Build a downloadable PDF report from analysis results."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm, topMargin=16 * mm, bottomMargin=16 * mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=9, leading=12, textColor=colors.HexColor("#475569")))
    story = [
        Paragraph("ResumeAI Analysis Report", styles["Title"]),
        Paragraph("AI-powered resume analysis for smarter job applications", styles["Small"]),
        Spacer(1, 8 * mm),
        Paragraph(f"<b>Candidate:</b> {result['profile']['name']}", styles["BodyText"]),
        Paragraph(f"<b>Resume:</b> {result['resume_name']}", styles["BodyText"]),
        Paragraph(f"<b>Overall Match:</b> {result['scores']['overall']}%", styles["Heading2"]),
        Spacer(1, 4 * mm),
    ]

    score_rows = [["Category", "Score"]] + [[label.title(), f"{result['scores'][key]}%"] for key, label in [
        ("skills", "Skills Match"), ("keywords", "Keyword Match"), ("experience", "Experience"),
        ("education", "Education"), ("projects", "Project Relevance")]]
    table = Table(score_rows, colWidths=[110 * mm, 45 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story += [table, Spacer(1, 7 * mm)]

    def bullet_section(title: str, items: list[str]):
        story.append(Paragraph(title, styles["Heading2"]))
        if not items:
            story.append(Paragraph("None detected.", styles["Small"]))
        else:
            for item in items:
                story.append(Paragraph(f"• {item}", styles["BodyText"]))
        story.append(Spacer(1, 3 * mm))

    bullet_section("Matched Skills", result["matched_skills"])
    bullet_section("Missing Skills", result["missing_skills"])
    bullet_section("ATS Keywords Missing", result["keyword_analysis"]["missing"])
    bullet_section("Recommendations", result["recommendations"])
    bullet_section("Skills to Learn", [f"{x['priority']}: {x['skill']} — {x['reason']}" for x in result["skills_to_learn"]])

    story.append(Paragraph("Methodology", styles["Heading2"]))
    story.append(Paragraph("This is an estimated portfolio-style matching score, not the exact score of a real company's ATS. The default weighting is 50% skills, 20% keywords, 15% experience, 10% education and 5% project relevance.", styles["Small"]))
    doc.build(story)
    return buffer.getvalue()
