import re
import PyPDF2
from typing import Dict, Any, List

RESUME_SECTIONS = [
    "skills", "technical skills", "key skills",
    "core competencies", "technologies", "tools"
]

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception:
        return ""
    return text

def extract_email(text: str) -> str:
    email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return email.group(0) if email else ""

def extract_phone(text: str) -> str:
    phone = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    return phone.group(0) if phone else ""

def extract_name(text: str) -> str:
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines:
        if (line.istitle() or line.isupper()) and len(line.split()) in (2, 3):
            if not any(word in line.lower() for word in ["phone", "email", "linkedin"]):
                return line
    return "Unknown"

def extract_skills(text: str) -> List[str]:
    if not text:
        return []
    
    text_lower = text.lower()
    skill_text = ""
    
    for section in RESUME_SECTIONS:
        if section in text_lower:
            start = text_lower.index(section) + len(section)
            skill_text = text[start:].split('\n')[0]
            break
    
    if not skill_text:
        bullet_points = re.findall(r"(?:^|\n)\s*[•\-*]\s*(.*)", text)
        skill_text = " ".join(bullet_points)
    
    skills = re.split(r"[,\n;/&+]", skill_text)
    cleaned = []
    
    for skill in skills:
        skill = skill.strip()
        skill = re.sub(r"[^\w\s+#-]", "", skill)
        skill = re.sub(r"\s+", " ", skill).strip()
        if skill and len(skill) > 2 and not skill.isdigit():
            cleaned.append(skill.lower())
    
    return list(set(cleaned))

def parse_resume(pdf_path: str) -> Dict[str, Any]:
    try:
        text = extract_text_from_pdf(pdf_path)
        return {
            "name": extract_name(text),
            "email": extract_email(text),
            "phone": extract_phone(text),
            "skills": extract_skills(text),
            "raw_text": text
        }
    except Exception:
        return {
            "name": "Unknown",
            "email": "",
            "phone": "",
            "skills": [],
            "raw_text": ""
        }