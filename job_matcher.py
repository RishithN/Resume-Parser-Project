import re
from difflib import SequenceMatcher

# --- JD Skill Extraction ---
def clean_and_split_skills(text: str) -> list:
    if not text:
        return []

    text = text.lower()
    text = re.sub(r"[\n;/]", ",", text)
    text = re.sub(r"\band\b", ",", text)

    skills = [s.strip() for s in text.split(",") if s.strip()]
    skills = [re.sub(r"[^\w\+\# ]", "", s).strip() for s in skills]

    blacklist = {
        "required", "skills", "responsibilities", "qualifications",
        "key", "experience", "about", "role", "requirements",
        "preferred", "technologies", "tools"
    }
    skills = [s for s in skills if s and s not in blacklist]

    return list(set(skills))


# --- Matching Logic ---
def text_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def get_resume_match_score(resume_data, jd_text, resume_skills, jd_skills) -> dict:
    jd_set = set(jd_skills)
    resume_set = set(resume_skills)

    matched = sorted(list(jd_set & resume_set))
    missing = sorted(list(jd_set - resume_set))

    # fuzzy keyword matching
    matched_keywords = []
    for r in resume_set:
        for j in jd_set:
            if text_similarity(r, j) > 0.85 and j not in matched_keywords:
                matched_keywords.append(j)

    skill_score = round((len(matched) / len(jd_set)) * 100, 2) if jd_set else 0
    similarity_score = round(
        sum(text_similarity(r, j) for r in resume_set for j in jd_set) / (len(resume_set) * len(jd_set)),
        2
    ) if jd_set and resume_set else 0
    final_score = round((skill_score * 0.7 + similarity_score * 30), 2)

    return {
        "resume_name": resume_data.get("name", "Unknown"),
        "matched_skills": matched,
        "missing_skills": missing,
        "matched_keywords": matched_keywords,
        "skill_score": skill_score,
        "similarity_score": similarity_score,
        "final_score": final_score,
    }
