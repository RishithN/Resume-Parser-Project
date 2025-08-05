from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_resume_match_score(resume_text, resume_skills, jd_text):
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform([resume_text, jd_text])
    similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100

    jd_text_lower = jd_text.lower()
    jd_keywords = [word for word in jd_text_lower.split() if len(word) > 2]
    matched_keywords = [word for word in jd_keywords if word in resume_text.lower()]

    matched_skills = [skill for skill in resume_skills if skill.lower() in jd_text_lower]
    missing_skills = list(set(resume_skills) - set(matched_skills))

    skill_score = (len(matched_skills) / len(resume_skills) * 100) if resume_skills else 0
    final_score = (0.6 * similarity_score) + (0.4 * skill_score)

    return {
        "similarity_score": similarity_score,
        "skill_score": skill_score,
        "final_score": final_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_keywords": list(set(matched_keywords))
    }
