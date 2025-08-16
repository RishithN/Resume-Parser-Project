import re
from difflib import SequenceMatcher
from typing import List, Dict, Set, Any

JD_SKILL_SECTIONS = [
    "required skills", "requirements", "qualifications",
    "technical skills", "must have", "nice to have"
]

def extract_jd_skills(jd_text: str) -> List[str]:
    if not jd_text:
        return []
    
    text_lower = jd_text.lower()
    skill_section = ""
    
    for section in JD_SKILL_SECTIONS:
        if section in text_lower:
            start = text_lower.index(section) + len(section)
            skill_section = jd_text[start:].split('\n')[0]
            break
    
    if not skill_section:
        skill_section = jd_text
    
    skills = re.split(r"[,\n;/&+]", skill_section)
    cleaned = []
    
    for skill in skills:
        skill = skill.strip().lower()
        skill = re.sub(r"[^\w\s+#-]", "", skill)
        skill = re.sub(r"\s+", " ", skill).strip()
        if skill and len(skill) > 2 and not skill.isdigit():
            cleaned.append(skill)
    
    return list(set(cleaned))

def get_resume_match_score(
    resume_data: Dict[str, Any],
    jd_text: str,
    resume_skills: List[str],
    jd_skills: List[str] = None
) -> Dict[str, Any]:
    if jd_skills is None:
        jd_skills = extract_jd_skills(jd_text)
    
    jd_set = set(jd_skills)
    resume_set = set(resume_skills)
    
    matched = sorted(jd_set & resume_set)
    missing = sorted(jd_set - resume_set)
    
    skill_score = (len(matched) / len(jd_set)) * 100 if jd_set else 0
    
    resume_words = set(re.findall(r'\w+', resume_data.get('raw_text', '').lower()))
    jd_words = set(re.findall(r'\w+', jd_text.lower()))
    similarity_score = (len(resume_words & jd_words) / len(jd_words)) * 100 if jd_words else 0
    
    final_score = (skill_score * 0.7) + (similarity_score * 0.3)
    
    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_score": round(skill_score, 1),
        "similarity_score": round(similarity_score, 1),
        "final_score": round(final_score, 1)
    }