from models.scoring import calculate_scores
from services.job_analyzer import keyword_match, compare_skills


def test_score_weights():
    scores = calculate_scores(100, 100, "internship experience", "B.Tech Computer Science", "Python project")
    assert 0 <= scores["overall"] <= 100
    assert scores["skills"] == 100


def test_keyword_matching():
    result = keyword_match("python sql git", ["python", "sql", "docker"])
    assert result["found"] == ["python", "sql"]
    assert result["missing"] == ["docker"]


def test_skill_comparison():
    result = compare_skills(["Python", "Git"], ["Python", "Docker", "Git"])
    assert "Python" in result["matched"]
    assert "Docker" in result["missing"]
