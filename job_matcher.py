import re
from difflib import SequenceMatcher
from typing import List, Dict, Set, Any

# Constants
SKILL_THRESHOLD = 0.85
JD_SKILL_SECTIONS = [
    "required skills", "requirements", "qualifications",
    "technical skills", "must have", "nice to have"
]

def extract_jd_skills(jd_text: str) -> List[str]:
    """Extract skills from job description text"""
    if not jd_text:
        return []
    
    # Find skills section
    jd_lower = jd_text.lower()
    skill_section = ""
    
    for section in JD_SKILL_SECTIONS:
        if section in jd_lower:
            start = jd_lower.index(section) + len(section)
            # Get text until next section or end
            skill_section = jd_text[start:].split('\n')[0]
            break
    
    # Fallback to entire JD if no section found
    if not skill_section:
        skill_section = jd_text
    
    # Split into individual skills
    skills = re.split(r"[,\n;/&+]", skill_section)
    cleaned_skills = []
    
    for skill in skills:
        skill = skill.strip().lower()
        # Remove special chars but keep + and #
        skill = re.sub(r"[^\w\s+#-]", "", skill)
        skill = re.sub(r"\s+", " ", skill).strip()
        
        # Filter out empty and very short skills
        if skill and len(skill) > 2 and not skill.isdigit():
            cleaned_skills.append(skill)
    
    return list(set(cleaned_skills))  # Remove duplicates

def skill_similarity(skill1: str, skill2: str) -> float:
    """Calculate similarity between two skills (0-1)"""
    return SequenceMatcher(None, skill1.lower(), skill2.lower()).ratio()

def get_resume_match_score(
    resume_data: Dict[str, Any],
    jd_text: str,
    resume_skills: List[str],
    jd_skills: List[str] = None
) -> Dict[str, Any]:
    """
    Calculate matching scores between resume and JD
    Returns:
        {
            "matched_skills": List[str],
            "missing_skills": List[str],
            "skill_score": float (0-100),
            "final_score": float (0-100)
        }
    """
    # Extract JD skills if not provided
    if jd_skills is None:
        jd_skills = extract_jd_skills(jd_text)
    
    jd_skills_set = set(jd_skills)
    resume_skills_set = set(resume_skills)
    
    # Exact matches
    matched_skills = sorted(jd_skills_set & resume_skills_set)
    missing_skills = sorted(jd_skills_set - resume_skills_set)
    
    # Fuzzy matches
    fuzzy_matches = []
    for jd_skill in jd_skills_set:
        for resume_skill in resume_skills_set:
            if skill_similarity(jd_skill, resume_skill) >= SKILL_THRESHOLD:
                fuzzy_matches.append(jd_skill)
                break
    
    # Calculate scores
    skill_score = (len(matched_skills) / len(jd_skills_set)) * 100 if jd_skills_set else 0
    
    # Text similarity (simple word overlap)
    resume_words = set(re.findall(r'\w+', resume_data.get('raw_text', '').lower())
    jd_words = set(re.findall(r'\w+', jd_text.lower()))
    common_words = resume_words & jd_words
    similarity_score = (len(common_words) / len(jd_words)) * 100 if jd_words else 0
    
    # Combined score (weighted average)
    final_score = (skill_score * 0.7) + (similarity_score * 0.3)
    
    return {
        "matched_skills": matched_skills + fuzzy_matches,
        "missing_skills": missing_skills,
        "skill_score": round(skill_score, 1),
        "similarity_score": round(similarity_score, 1),
        "final_score": round(final_score, 1)
    }