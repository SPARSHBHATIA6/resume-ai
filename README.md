# ResumeAI — AI-Powered Resume Analyzer

ResumeAI is a polished, beginner-friendly Streamlit application that compares a PDF resume with a target job description. It extracts skills, performs ATS-style keyword analysis, calculates a transparent match score, identifies skill gaps, suggests resume improvements, and generates a professional PDF report.

> **Portfolio note:** The score is an educational/portfolio-style estimate. It is **not** the exact score used by a real company's ATS.

## ✨ Features

- Drag-and-drop PDF resume upload with validation
- Text extraction with `pypdf`
- Name, contact, education, skills, projects, experience and certifications detection
- Predefined technical skill database in `data/skills.json`
- Job-description skill extraction
- Matched / missing skill chips
- Transparent weighted match score
- ATS-style keyword analysis
- TF-IDF semantic similarity
- Project and resume improvement suggestions
- Prioritized skills-to-learn list
- Professional dashboard with Plotly charts
- Light/dark mode
- Demo mode with sample resume + job description
- SQLite analysis metadata history
- Professional downloadable PDF report
- Optional OpenAI recommendations
- Unit tests with pytest
- Privacy-first design: uploaded PDFs are not permanently stored

## 🧱 Tech stack

- **UI:** Streamlit + custom CSS
- **Backend:** Python
- **PDF:** pypdf
- **Data:** Pandas, NumPy
- **NLP / matching:** scikit-learn, regex-based extraction; spaCy is available for future NLP expansion
- **Visualization:** Plotly
- **Database:** SQLite
- **Reports:** ReportLab
- **Optional AI:** OpenAI API
- **Testing:** pytest

## 🚀 Run locally

```bash
git clone <your-repository-url>
cd resume-ai
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in your terminal.

## 🤖 Optional AI mode

The application works without an API key. To enable advanced AI recommendations:

1. Copy `.env.example` to `.env`.
2. Add your key:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

3. Restart Streamlit.

Never commit `.env` to GitHub. It is already listed in `.gitignore`.

## 📊 Scoring methodology

Default weights:

| Component | Weight |
|---|---:|
| Skills Match | 50% |
| Keyword Match | 20% |
| Experience | 15% |
| Education | 10% |
| Project Relevance | 5% |

The score is intentionally transparent so a beginner can inspect and improve the logic. Experience, education and project scores use lightweight section-completeness heuristics; they should not be interpreted as hiring decisions.

## 🧠 How it works

1. User uploads a PDF.
2. `services/pdf_parser.py` extracts text.
3. `services/skill_extractor.py` detects contacts, sections and known skills.
4. `services/job_analyzer.py` extracts job skills, keywords and TF-IDF similarity.
5. `models/scoring.py` calculates the weighted score.
6. `services/recommendations.py` creates rule-based advice.
7. Optional `services/ai_service.py` calls an LLM only when an API key is configured.
8. `reports/pdf_report.py` creates the downloadable report.
9. `database/db.py` stores analysis metadata only.

## 🗂️ Project structure

```text
resume-ai/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── LICENSE
├── data/
│   └── skills.json
├── database/
│   └── db.py
├── models/
│   └── scoring.py
├── services/
│   ├── pdf_parser.py
│   ├── skill_extractor.py
│   ├── job_analyzer.py
│   ├── recommendations.py
│   └── ai_service.py
├── utils/
│   ├── text_processing.py
│   └── validators.py
├── reports/
│   └── pdf_report.py
├── assets/
├── screenshots/
└── tests/
    ├── test_parser.py
    ├── test_skills.py
    └── test_scoring.py
```

## 🧪 Testing

Run:

```bash
pytest -q
```

## 🔐 Privacy

Your resume is processed for analysis. Do not upload resumes containing information you are not comfortable processing.

ResumeAI does not permanently store uploaded PDF files. SQLite stores analysis metadata such as the resume filename, score and matched/missing skill names.

## 🧭 Roadmap

- [x] V1: PDF extraction, skill extraction, matching, dashboard
- [x] V2: NLP similarity, ATS analysis, PDF report
- [x] V3 foundation: optional LLM recommendations
- [ ] V3: AI resume rewriting
- [ ] V4: Multiple job comparison
- [ ] V4: Resume version tracking
- [ ] V5: Cloud deployment
- [ ] V5: User accounts and cloud history

## 📸 Screenshots

Add screenshots or a demo GIF to `screenshots/` after running the application. Recommended captures:

- Landing page
- Analyze page
- Dashboard overview
- ATS analysis
- Downloaded report

## 💼 GitHub presentation

Suggested repository description:

> AI-powered resume analyzer that compares resumes with job descriptions, detects skill gaps, performs ATS-style keyword analysis, and provides actionable improvement recommendations.

Suggested topics:

`python` `machine-learning` `nlp` `resume-analyzer` `artificial-intelligence` `streamlit` `scikit-learn` `spacy` `ats` `career-tools`

## 🤝 Contributing

Fork the project, create a feature branch, add tests for behavior changes, and open a pull request with a clear explanation.

## 📄 License

MIT License.
