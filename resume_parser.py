import re
import PyPDF2
from typing import Dict, Any, List

# Constants
RESUME_SKILL_SECTIONS = [
    "skills", "technical skills", "key skills",
    "core competencies", "technologies"
]

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        raise Exception(f"PDF extraction failed: {str(e)}")
    return text

def extract_email(text: str) -> str:
    """Extract email address from text"""
    email = re.search(r"[\w.-]+@[\w.-]+\.\w+", text)
    return email.group(0) if email else ""

def extract_phone(text: str) -> str:
    """Extract phone number from text"""
    phone = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    return phone.group(0) if phone else ""

def extract_name(text: str) -> str:
    """Extract candidate name from text"""
    # Look for the first line with title case that's not too long
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines:
        if (line.istitle() or line.isupper()) and len(line.split()) <= 4:
            return line
    return "Unknown"

def extract_skills(text: str) -> List[str]:
    """Extract skills from resume text"""
    if not text:
        return []
    
    # Find skills section
    text_lower = text.lower()
    skill_section = ""
    
    for section in RESUME_SKILL_SECTIONS:
        if section in text_lower:
            start = text_lower.index(section) + len(section)
            skill_section = text[start:].split('\n')[0]
            break
    
    if not skill_section:  # Fallback to bullet points
        bullet_points = re.findall(r"(?:^|\n)\s*[•\-*]\s*(.*)", text)
        skill_section = " ".join(bullet_points)
    
    # Extract individual skills
    skill_list = re.split(r"[,\n;/&+]", skill_section)
    skills = []
    
    for skill in skill_list:
        skill = skill.strip()
        if skill and len(skill) > 2:  # Filter very short strings
            skills.append(skill)
    
    return list(set(skills))  # Remove duplicates

def parse_resume(pdf_path: str) -> Dict[str, Any]:
    """Main function to parse resume PDF"""
    try:
        text = extract_text_from_pdf(pdf_path)
        return {
            "name": extract_name(text),
            "email": extract_email(text),
            "phone": extract_phone(text),
            "skills": extract_skills(text),
            "raw_text": text
        }
    except Exception as e:
        return {
            "name": "Unknown",
            "email": "",
            "phone": "",
            "skills": [],
            "raw_text": ""
        }