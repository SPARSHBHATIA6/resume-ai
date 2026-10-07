from services.skill_extractor import extract_skills, extract_contact_info


def test_skill_extraction():
    skills = extract_skills("Python, Pandas, NumPy, Machine Learning, Git and Docker")
    assert "Python" in skills
    assert "Pandas" in skills
    assert "Machine Learning" in skills
    assert "Docker" in skills


def test_contact_extraction():
    data = extract_contact_info("hello me@example.com github.com/user")
    assert data["email"] == "me@example.com"
    assert "github.com/user" in data["github"]
