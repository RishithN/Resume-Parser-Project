import re
import spacy
from typing import Dict

# Load small English model
nlp = spacy.load("en_core_web_sm")

# Stopwords & junk words to filter out from skills
STOPWORDS_RESUME = {
    "experience", "responsibilities", "requirement", "requirements",
    "knowledge", "ability", "skills", "proficiency", "capability",
    "competency", "project", "role", "objective", "summary"
}


def clean_text(text: str) -> str:
    """Basic cleaning of resume text"""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\+\# ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_name(doc):
    """Try extracting candidate name (first PROPN sequence)."""
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None


def extract_email(text):
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text):
    match = re.search(r"\+?\d[\d\s\-]{8,15}", text)
    return match.group(0) if match else None


def extract_skills(text):
    """Naive skill extraction by keyword spotting."""
    tokens = clean_text(text).split()
    skills = set()

    for token in tokens:
        if len(token) > 1 and token not in STOPWORDS_RESUME:
            # Keep technical tokens like python, c++, node.js, etc.
            if re.match(r"[a-z\+\#]+", token):
                skills.add(token)

    return sorted(skills)


def parse_resume(text: str) -> Dict:
    """Main entry to parse resume text into structured info."""
    if not text:
        return {}

    doc = nlp(text)

    name = extract_name(doc)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "raw_text": text
    }
