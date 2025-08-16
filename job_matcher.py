import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def clean_and_split_skills(text: str) -> list:
    """Extracts possible skills dynamically from JD or resume text."""
    if not text:
        return []

    text = text.lower()

    # Remove common headers/phrases before splitting
    noise_patterns = [
        r"skills required.*?:", r"requirements.*?:", r"responsibilities.*?:",
        r"qualifications.*?:", r"preferred.*?:"
    ]
    for pattern in noise_patterns:
        text = re.sub(pattern, "", text)

    text = re.sub(r"[\n;/]", ",", text)
    text = re.sub(r"\band\b", ",", text)

    # Split into chunks
    skills = [s.strip() for s in text.split(",") if s.strip()]
    skills = [re.sub(r"[^\w\+\# ]", "", s).strip() for s in skills]

    # Blacklist common words that sneak in
    blacklist = {
        "required", "skills", "responsibilities", "qualifications",
        "key", "experience", "about", "role", "requirements",
        "preferred", "technologies", "tools"
    }
    skills = [s for s in skills if s and s not in blacklist]

    return list(set(skills))


def calculate_text_similarity(resume_text: str, jd_text: str) -> float:
    """Calculates cosine similarity between resume and job description text."""
    if not resume_text or not jd_text:
        return 0.0

    vectorizer = TfidfVectorizer().fit([resume_text, jd_text])
    vectors = vectorizer.transform([resume_text, jd_text])
    similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round(similarity * 100, 2)


def get_resume_match_score(resume_data: dict, jd_text: str) -> dict:
    """Matches resume skills with job description skills and calculates score."""

    # Extract JD skills
    jd_skills = clean_and_split_skills(jd_text)

    # Extract Resume skills
    raw_resume_skills = resume_data.get("skills", [])
    resume_skills = [
        re.sub(r"[^\w\+\# ]", "", s.lower()).strip()
        for s in raw_resume_skills
    ]
    resume_skills = list(set([s for s in resume_skills if s]))

    # Sets for comparison
    jd_set = set(jd_skills)
    resume_set = set(resume_skills)

    matched = sorted(list(jd_set & resume_set))
    missing = sorted(list(jd_set - resume_set))

    # Skill-based score
    skill_score = round((len(matched) / len(jd_set)) * 100, 2) if jd_set else 0

    # Text similarity score (optional, for app.py)
    resume_text = resume_data.get("text", "")
    similarity_score = calculate_text_similarity(resume_text, jd_text)

    return {
        "resume_name": resume_data.get("name", "Unknown"),
        "extracted_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_score": skill_score,
        "similarity_score": similarity_score
    }
