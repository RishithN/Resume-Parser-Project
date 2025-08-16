# job_matcher.py
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def clean_text(text: str) -> str:
    """Basic text cleanup for NLP."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\+\#]", " ", text)  # keep +, # for C++, C#
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_resume_match_score(resume_data: dict, jd_text: str) -> dict:
    """
    Compare resume with job description and compute similarity/skill scores.
    Returns dict with similarity, skill overlap, final score, and matched tokens.
    """

    # Extract resume skills safely
    resume_skills = resume_data.get("skills", []) or []
    resume_skills = [s.lower().strip() for s in resume_skills if s]
    resume_text = clean_text(resume_data.get("raw_text", ""))

    # Clean JD
    jd_text_clean = clean_text(jd_text)

    # --- Similarity score using TF-IDF ---
    similarity_score = 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text_clean])
        similarity_score = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100)
    except Exception:
        similarity_score = 0.0

    # --- Extract keywords from JD (rough skill keywords) ---
    jd_tokens = set(jd_text_clean.split())
    resume_tokens = set(resume_text.split())

    matched_keywords = sorted(list(jd_tokens & resume_tokens))

    # --- Skill match score ---
    jd_keywords = [tok for tok in jd_tokens if len(tok) > 2]  # filter junk
    jd_skill_set = set(jd_keywords)
    resume_skill_set = set(resume_skills)

    matched_skills = sorted(list(jd_skill_set & resume_skill_set))
    missing_skills = sorted(list(jd_skill_set - resume_skill_set))

    # --- Final skill score ---
    if jd_skill_set:
        skill_score = round(len(matched_skills) / len(jd_skill_set) * 100, 2)
    else:
        skill_score = 0.0

    # --- Final weighted score (50% skills, 50% similarity) ---
    final_score = round((skill_score * 0.5) + (similarity_score * 0.5), 2)

    return {
        "similarity_score": similarity_score,
        "skill_score": skill_score,
        "final_score": final_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_keywords": matched_keywords
    }
