import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Utility: clean text ---
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\+\# ]+", " ", text)  # keep alnum, +, #
    text = re.sub(r"\s+", " ", text).strip()
    return text


# --- Remove noisy words often seen in job descriptions ---
STOPWORDS_JD = {
    "required", "requirements", "responsibilities", "preferred",
    "experience", "skills", "knowledge", "proficiency",
    "ability", "capabilities", "competencies"
}


def preprocess_jd_text(jd_text: str) -> str:
    jd_text = clean_text(jd_text)
    tokens = [t for t in jd_text.split() if t not in STOPWORDS_JD]
    return " ".join(tokens)


# --- Cosine similarity on cleaned text ---
def compute_text_similarity(text1: str, text2: str) -> float:
    text1, text2 = clean_text(text1), clean_text(text2)
    if not text1 or not text2:
        return 0.0
    vect = TfidfVectorizer().fit([text1, text2])
    tfidf = vect.transform([text1, text2])
    return cosine_similarity(tfidf[0], tfidf[1])[0][0]


# --- Skill match score ---
def compute_skill_match(jd_skills, resume_skills) -> float:
    if not jd_skills or not resume_skills:
        return 0.0
    jd_set = set(s.lower() for s in jd_skills)
    resume_set = set(s.lower() for s in resume_skills)
    match_count = len(jd_set & resume_set)
    return match_count / len(jd_set) if jd_set else 0.0


# --- Final resume match function ---
def get_resume_match_score(jd_text, jd_skills, resume_data):
    """
    jd_text    : full job description (string)
    jd_skills  : list of skills extracted from JD
    resume_data: dict { "name","email","phone","skills","raw_text" }
    """

    # Clean JD text
    jd_text_cleaned = preprocess_jd_text(jd_text)

    # Use only skills + experience portions of resume for text sim
    resume_focus_text = " ".join(resume_data.get("skills", [])) or resume_data.get("raw_text", "")

    # Text similarity
    text_sim = compute_text_similarity(jd_text_cleaned, resume_focus_text)

    # Skill match
    skill_match = compute_skill_match(jd_skills, resume_data.get("skills", []))

    # Weighted final score
    final_score = (0.4 * text_sim * 100) + (0.6 * skill_match * 100)

    # Match quality bucket
    if final_score >= 70:
        quality = "High"
    elif final_score >= 50:
        quality = "Medium"
    else:
        quality = "Low"

    return {
        "name": resume_data.get("name"),
        "email": resume_data.get("email"),
        "phone": resume_data.get("phone"),
        "text_similarity": round(text_sim * 100, 2),
        "skill_match": round(skill_match * 100, 2),
        "final_score": round(final_score, 2),
        "match_quality": quality,
    }
