import re
import PyPDF2
from typing import Dict, Any, List

# Constants
RESUME_SECTIONS = [
    "skills", "technical skills", "key skills",
    "core competencies", "technologies", "tools"
]

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from PDF file"""
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        raise Exception(f"Failed to read PDF: {str(e)}")
    return text

def extract_email(text: str) -> str:
    """Extract email address from text"""
    email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return email.group(0) if email else ""

def extract_phone(text: str) -> str:
    """Extract phone number from text"""
    phone = re.search(
        r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        text
    )
    return phone.group(0) if phone else ""

def extract_name(text: str) -> str:
    """Extract candidate name from resume text"""
    # Look for the first line that appears to be a name
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for line in lines:
        # Simple heuristics for name detection
        if (line.istitle() or line.isupper()) and len(line.split()) in (2, 3):
            if not any(word in line.lower() for word in ["phone", "email", "linkedin"]):
                return line
    
    return "Unknown"

def extract_skills(text: str) -> List[str]:
    """Extract skills from resume text"""
    if not text:
        return []
    
    # Try to find skills section
    text_lower = text.lower()
    skill_text = ""
    
    for section in RESUME_SECTIONS:
        if section in text_lower:
            start = text_lower.index(section) + len(section)
            # Get text until next section
            skill_text = text[start:].split('\n')[0]
            break
    
    # Fallback to bullet points if no section found
    if not skill_text:
        bullet_points = re.findall(r"(?:^|\n)\s*[•\-*]\s*(.*)", text)
        skill_text = " ".join(bullet_points)
    
    # Split into individual skills
    skills = re.split(r"[,\n;/&+]", skill_text)
    cleaned_skills = []
    
    for skill in skills:
        skill = skill.strip()
        # Basic cleaning
        skill = re.sub(r"[^\w\s+#-]", "", skill)
        skill = re.sub(r"\s+", " ", skill).strip()
        
        # Filter out empty and invalid skills
        if skill and len(skill) > 2 and not skill.isdigit():
            cleaned_skills.append(skill.lower())
    
    return list(set(cleaned_skills))  # Remove duplicates

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