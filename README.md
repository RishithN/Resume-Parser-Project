# Resume-Parser-Project
 This is a resume analyzer which matches multiple resumes based on the job description, mentions the skills, matched skills and missed skills accoding to the job description and also give the skill match and final match percentage, resume quality score as well as the feedback of the resume
# Resume Parser with Keyword & JD Matching

This project extracts resume data from PDFs, compares skills and text with a job description, calculates match scores, visualizes results, and ranks candidates.

### 🔍 Features:
- Resume parsing (name, email, phone, skills)
- JD text similarity using TF-IDF
- Skill match scoring
- Resume quality analyzer
- Shortlist candidates by match %
- Visual dashboards via Streamlit
- Email notification to shortlisted (optional)

### 🛠 Tech Stack:
- Python
- Streamlit
- scikit-learn
- PyPDF2
- Pandas
- Regex

### 📂 How to Run:

```bash
pip install -r requirements.txt
streamlit run app.py
