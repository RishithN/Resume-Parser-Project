import re
import PyPDF2

# --- PDF text extraction ---
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    return text


# --- Simple field extraction ---
def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else None


def extract_phone(text):
    match = re.search(r'\+?\d[\d\s\-]{8,15}\d', text)
    return match.group(0) if match else None


def extract_name(text):
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    return lines[0] if lines else "Unknown"


# --- Skills (Dynamic) ---
START_KEYS_RESUME = [
    "skills", "technical skills", "skills summary", "core competencies",
    "technologies", "tools", "tech stack"
]
STOP_KEYS = [
    "experience", "work experience", "professional experience", "projects",
    "education", "certifications", "achievements", "summary", "profile"
]
SEP_PATTERN = r"[,\n;/\|\&•·]+"


def normalize_skill_token(tok: str) -> str:
    if not tok:
        return ""
    s = tok.lower().strip()
    s = re.sub(r"(?<=\w)-(?=\w)", " ", s)  # deep-learning -> deep learning
    s = re.sub(r"[^\w\s\+\#]", " ", s)     # keep alphanum, +, #
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_section(text: str, start_keys, stop_keys) -> str:
    if not text:
        return ""
    low = text.lower()
    start_pos = None
    for key in start_keys:
        m = re.search(rf"\b{re.escape(key)}\b\s*[:\-]?", low)
        if m:
            start_pos = m.end()
            break
    if start_pos is None:
        return ""

    stop_positions = []
    for key in stop_keys:
        m = re.search(rf"\n\s*\b{re.escape(key)}\b", low[start_pos:])
        if m:
            stop_positions.append(start_pos + m.start())
    end_pos = min(stop_positions) if stop_positions else len(text)
    return text[start_pos:end_pos]


def extract_skills(text):
    text = text or ""
    chunk = extract_section(text, START_KEYS_RESUME, STOP_KEYS)
    if not chunk:
        chunk = text

    paren_tokens = [m.group(1).strip() for m in re.finditer(r"\((.*?)\)", chunk)]
    raw_tokens = re.split(SEP_PATTERN, chunk)
    raw_tokens += paren_tokens

    skills = []
    for tok in raw_tokens:
        tok = tok.strip()
        if not tok:
            continue
        tok = re.sub(r"\band\b", ",", tok, flags=re.I)
        for sub in [s.strip() for s in tok.split(",") if s.strip()]:
            norm = normalize_skill_token(sub)
            if norm and len(norm) > 1:
                skills.append(norm)

    seen, uniq = set(), []
    for s in skills:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq


def parse_resume(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),   # list[str]
        "raw_text": text
    }
