import streamlit as st
import os
import tempfile
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import re
from typing import List, Dict, Any, Optional, Tuple

# Configure page
st.set_page_config(
    page_title="📄 Resume Matcher", 
    layout="centered", 
    initial_sidebar_state="expanded"
)

# Display header
st.markdown("""
# 📄 Resume Parser & JD Matcher

Match multiple resumes against job_description.txt  
Get detailed matching analysis with skills comparison.

---
""")

# Initialize NLTK
try:
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception:
    pass

# Import local modules
try:
    from resume_parser import parse_resume
    from job_matcher import get_resume_match_score, extract_jd_skills
except ImportError as e:
    st.error(f"Failed to import local modules: {str(e)}")
    st.stop()

# Constants
JD_FILE = "job_description.txt"
SKILL_THRESHOLD = 0.85
MIN_WORD_COUNT = 100

def match_label(score: float) -> str:
    if score >= 70: return "🟢 High"
    if score >= 40: return "🟡 Medium"
    return "🔴 Low"

def analyze_resume_quality(data: Dict[str, Any]) -> Tuple[int, str]:
    score = 0
    feedback = []
    
    if data.get('name'): score += 10
    else: feedback.append("Missing Name")
    
    if data.get('email'): score += 10
    else: feedback.append("Missing Email")
    
    if data.get('phone'): score += 10
    else: feedback.append("Missing Phone")
    
    if data.get('skills'): score += 10
    else: feedback.append("Missing Skills")
    
    word_count = len(data.get('raw_text', '').split())
    if word_count < MIN_WORD_COUNT:
        feedback.append(f"Too Short (<{MIN_WORD_COUNT} words)")
    elif word_count <= 250: score += 10
    else: score += 20
    
    sections = ["education", "experience", "skills", "projects"]
    found = [s for s in sections if s in data.get('raw_text', '').lower()]
    score += len(found) * 10
    
    if missing := list(set(sections) - set(found)):
        feedback.append(f"Missing: {', '.join(missing)}")
    
    if score >= 90: summary = "✅ Excellent"
    elif score >= 70: summary = "👍 Good"
    elif score >= 50: summary = "⚠️ Needs Work"
    else: summary = "❌ Poor"
    
    return score, f"{summary} | {'; '.join(feedback)}"

def load_jd_skills() -> Tuple[str, List[str]]:
    if not os.path.exists(JD_FILE):
        st.error(f"Job description file '{JD_FILE}' not found")
        st.stop()
    
    with open(JD_FILE, 'r', encoding='utf-8') as f:
        jd_text = f.read()
    
    return jd_text, extract_jd_skills(jd_text)

def main():
    jd_text, jd_skills = load_jd_skills()
    
    st.sidebar.markdown("### Job Description Info")
    st.sidebar.text(f"Skills extracted: {len(jd_skills)}")
    
    uploaded_resumes = st.file_uploader(
        "📄 Upload Resumes (PDF)", 
        type="pdf", 
        accept_multiple_files=True
    )
    
    if st.button("🔍 Analyze Resumes") and uploaded_resumes:
        start_time = time.time()
        results = []
        
        with st.spinner(f"Processing {len(uploaded_resumes)} resumes..."):
            for resume_file in uploaded_resumes:
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(resume_file.read())
                        tmp_path = tmp.name
                    
                    data = parse_resume(tmp_path)
                    resume_skills = [s.lower() for s in data.get('skills', [])]
                    
                    match = get_resume_match_score(
                        resume_data=data,
                        jd_text=jd_text,
                        resume_skills=resume_skills,
                        jd_skills=jd_skills
                    )
                    
                    quality_score, feedback = analyze_resume_quality(data)
                    
                    results.append({
                        "File": resume_file.name,
                        "Name": data.get('name'),
                        "Email": data.get('email'),
                        "Phone": data.get('phone'),
                        "Skills": ', '.join(resume_skills),
                        "Matched Skills": ', '.join(match['matched_skills']),
                        "Missing Skills": ', '.join(match['missing_skills']),
                        "Skill Match %": match['skill_score'],
                        "Final Score": match['final_score'],
                        "Match Quality": match_label(match['final_score']),
                        "Resume Quality": quality_score,
                        "Feedback": feedback
                    })
                    
                except Exception as e:
                    st.error(f"Error processing {resume_file.name}: {str(e)}")
                finally:
                    try: os.remove(tmp_path)
                    except: pass
        
        if results:
            df = pd.DataFrame(results)
            df.sort_values("Final Score", ascending=False, inplace=True)
            df.insert(0, "Rank", range(1, len(df)+1))
            
            st.success(f"✅ Analysis completed in {time.time()-start_time:.1f}s")
            st.dataframe(df.style.format({
                "Skill Match %": "{:.1f}%",
                "Final Score": "{:.1f}%"
            }))
            
            # Export options
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "💾 Download CSV",
                csv,
                "resume_analysis_results.csv",
                "text/csv"
            )
        else:
            st.error("No results generated")

if __name__ == "__main__":
    main()