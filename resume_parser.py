import re
import PyPDF2

SKILL_SET = [
    "python", "java", "sql", "excel", "power bi", "tableau", "pandas",
    "numpy", "flask", "django", "machine learning", "data analysis"
]

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r'\+?\d[\d\s-]{8,13}\d', text)
    return match.group(0) if match else None

def extract_name(text):
    lines = text.strip().split('\n')
    if lines:
        return lines[0]
    return "Unknown"

def extract_skills(text):
    text = text.lower()
    found_skills = [skill for skill in SKILL_SET if skill in text]
    return list(set(found_skills))

def parse_resume(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "raw_text": text
    }
