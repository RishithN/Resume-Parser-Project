import re

def clean_and_split_skills(text: str) -> list:
    """Extracts possible skills from JD text dynamically."""
    if not text:
        return []
    
    # Lowercase everything
    text = text.lower()
    
    # Replace separators with commas
    text = re.sub(r"[\n;/]", ",", text)
    text = re.sub(r"\band\b", ",", text)  # handle "Python and SQL"
    
    # Split into chunks
    skills = [s.strip() for s in text.split(",") if s.strip()]
    
    # Normalize: remove punctuation except +, #
    skills = [re.sub(r"[^\w\+\# ]", "", s).strip() for s in skills]
    
    # Filter out generic non-skill words
    blacklist = {
        "required", "skills", "responsibilities", "qualifications",
        "key", "experience", "about", "role", "requirements",
        "preferred", "technologies", "tools"
    }
    skills = [s for s in skills if s and s not in blacklist]
    
    return list(set(skills))  # remove duplicates


def match_resume_with_jd(resume_data: dict, jd_text: str) -> dict:
    """Matches resume skills with job description skills and calculates score."""
    
    # Extract JD skills dynamically
    jd_skills = clean_and_split_skills(jd_text)
    
    # Extract Resume skills
    raw_resume_skills = resume_data.get("skills", [])
    resume_skills = [
        re.sub(r"[^\w\+\# ]", "", s.lower()).strip()
        for s in raw_resume_skills
    ]
    resume_skills = list(set([s for s in resume_skills if s]))
    
    # Compare sets
    jd_set = set(jd_skills)
    resume_set = set(resume_skills)
    
    matched = sorted(list(jd_set & resume_set))
    missing = sorted(list(jd_set - resume_set))
    
    # Score calculation
    score = round((len(matched) / len(jd_set)) * 100, 2) if jd_set else 0
    
    return {
        "resume_name": resume_data.get("name", "Unknown"),
        "extracted_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "score": score
    }
