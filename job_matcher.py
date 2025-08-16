# job_matcher.py
import re

# --- Normalization and blacklist ---
BLACKLIST = {
    "required", "skills", "responsibilities", "qualifications",
    "key", "experience", "about", "role", "requirements",
    "preferred", "technologies", "tools", "summary", "profile"
}

def normalize_token(tok: str) -> str:
    """Normalize a token: lowercase, strip punctuation, handle C++, C#, etc."""
    if not tok:
        return ""
    s = tok.lower().strip()
    s = re.sub(r"(?<=\w)-(?=\w)", " ", s)  # deep-learning -> deep learning
    s = re.sub(r"[^\w\s\+\#]", " ", s)     # keep alnum, +, #
    s = re.sub(r"\s+", " ", s).strip()
    return s

# --- JD Skill Extraction ---
def clean_and_split_skills(text: str) -> list:
    """Extracts possible skills from JD text dynamically."""
    if not text:
        return []
    
    # Normalize separators
    text = text.lower()
    text = re.sub(r"[\n;/]", ",", text)
    text = re.sub(r"\band\b", ",", text)

    # Split into tokens
    raw_tokens = [s.strip() for s in text.split(",") if s.strip()]

    skills = []
    for tok in raw_tokens:
        norm = normalize_token(tok)
        if norm and norm not in BLACKLIST and len(norm) > 1:
            skills.append(norm)

    # Deduplicate while preserving order
    seen, uniq = set(), []
    for s in skills:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq

# --- Resume vs JD Matching ---
def get_resume_match_score(resume_data: dict, jd_text: str) -> dict:
    """Matches resume skills with job description skills and calculates score."""
    
    jd_skills = clean_and_split_skills(jd_text)

    raw_resume_skills = resume_data.get("skills", [])
    resume_skills = [normalize_token(s) for s in raw_resume_skills if s]
    resume_skills = [s for s in resume_skills if s and s not in BLACKLIST]

    # Convert to sets for overlap
    jd_set = set(jd_skills)
    resume_set = set(resume_skills)

    matched = sorted(list(jd_set & resume_set))
    missing = sorted(list(jd_set - resume_set))

    score = round((len(matched) / len(jd_set)) * 100, 2) if jd_set else 0

    return {
        "resume_name": resume_data.get("name", "Unknown"),
        "extracted_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "score": score
    }
