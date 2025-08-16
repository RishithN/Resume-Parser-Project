import re
from difflib import SequenceMatcher
from typing import List, Dict, Set, Any

# Constants
SKILL_SIMILARITY_THRESHOLD = 0.85
JD_SKILL_SECTIONS = [
    "required skills", "requirements", "qualifications",
    "technical skills", "must have", "nice to have"
]

def clean_skill(skill: str) -> str:
    """Normalize a skill string"""
    skill = skill.lower().strip()
    skill = re.sub(r"[^\w\s+#-]", "", skill)  # Remove special chars
    skill = re.sub(r"\s+", " ", skill)       # Collapse whitespace
    return skill

def extract_jd_skills(jd_text: str) -> Set[str]:
    """Extract skills from job description text"""
    if not jd_text:
        return set()
    
    # Find skills section
    jd_lower = jd_text.lower()
    skill_section = ""
    
    for section in JD_SKILL_SECTIONS:
        if section in jd_lower:
            start = jd_lower.index(section) + len(section)
            skill_section = jd_text[start:].split("\n")[0]
            break
    
    if not skill_section:  # Fallback to whole JD
        skill_section = jd_text
    
    # Split into individual skills
    skill_list = re.split(r"[,\n;/&+]", skill_section)
    skills = set()
    
    for skill in skill_list:
        skill = clean_skill(skill)
        if skill and len(skill) > 2:  # Filter out very short strings
            skills.add(skill)
    
    return skills

def skill_similarity(skill1: str, skill2: str) -> float:
    """Calculate similarity between two skills"""
    return SequenceMatcher(None, skill1.lower(), skill2.lower()).ratio()

def get_resume_match_score(
    resume_data: Dict[str, Any],
    jd_text: str,
    resume_skills: Set[str],
    jd_skills: Set[str]
) -> Dict[str, Any]:
    """Calculate matching scores between resume and JD"""
    if not jd_skills:
        jd_skills = extract_jd_skills(jd_text)
    
    # Exact matches
    matched_skills = sorted(jd_skills & resume_skills)
    missing_skills = sorted(jd_skills - resume_skills)
    
    # Fuzzy matches
    matched_keywords = []
    for jd_skill in jd_skills:
        for resume_skill in resume_skills:
            if skill_similarity(jd_skill, resume_skill) > SKILL_SIMILARITY_THRESHOLD:
                matched_keywords.append(jd_skill)
                break
    
    # Calculate scores
    skill_score = (len(matched_skills) / len(jd_skills)) * 100 if jd_skills else 0
    
    # Text similarity (simplified)
    common_words = set(jd_text.lower().split()) & set(resume_data.get('raw_text', '').lower().split())
    similarity_score = (len(common_words) / len(set(jd_text.lower().split()))) * 100 if jd_text else 0
    
    # Combined score (weighted)
    final_score = (skill_score * 0.7) + (similarity_score * 0.3)
    
    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_keywords": list(set(matched_keywords)),  # Deduplicate
        "skill_score": round(skill_score, 1),
        "similarity_score": round(similarity_score, 1),
        "final_score": round(final_score, 1),
    }