from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_resume_match_score(resume_text, resume_skills, jd_text, jd_skills):
    """
    Compute:
    - TF-IDF cosine similarity between resume and JD
    - Skill match % = (# matched JD skills) / (# JD skills)
    - Final score = 0.6 * similarity + 0.4 * skill match
    """
    # --- Similarity (text) ---
    try:
        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform([resume_text or "", jd_text or ""])
        similarity_score = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100.0)
    except Exception:
        similarity_score = 0.0

    # --- Skills ---
    resume_skills_set = set([s.strip().lower() for s in (resume_skills or []) if s])
    jd_skills_set = set([s.strip().lower() for s in (jd_skills or []) if s])

    matched_skills = sorted(list(jd_skills_set & resume_skills_set))
    missing_skills = sorted(list(jd_skills_set - resume_skills_set))

    skill_score = (len(matched_skills) / len(jd_skills_set) * 100.0) if jd_skills_set else 0.0

    # --- Keywords (very light-weight) ---
    jd_tokens = [w for w in (jd_text or "").lower().split() if len(w) > 2]
    matched_keywords = sorted(list(set([w for w in jd_tokens if w in (resume_text or "").lower()])))

    final_score = 0.6 * similarity_score + 0.4 * skill_score

    return {
        "similarity_score": similarity_score,
        "skill_score": skill_score,
        "final_score": final_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_keywords": matched_keywords
    }
