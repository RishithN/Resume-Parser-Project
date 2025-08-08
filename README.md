# Resume-Parser-Project
A web-based tool that automates resume parsing, job description matching, and candidate ranking using NLP and machine learning techniques, allowing recruiters or hiring managers to efficiently shortlist the best-fit candidates.
# Resume Parser with Keyword & JD Matching

This project extracts resume data from PDFs, compares skills and text with a job description, calculates match scores, visualizes results, and ranks candidates.

### 🔍 Features:
- Resume parsing (name, email, phone, skills)
- JD text similarity using TF-IDF
- Auto-Ranking and Filtering
- Resume quality analyzer
- PDF Report Generator
- Visual dashboards via Streamlit
- Shortlisting and CSV export

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
