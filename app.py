import streamlit as st
import os
import tempfile
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import re
from typing import List, Dict, Any, Optional

# Configure page
st.set_page_config(
    page_title="📄 Resume Matcher", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# Display header
st.markdown("""
# 📄 Resume Parser & JD Matcher

Match multiple resumes against a job description using NLP.  
Get scores, preview results, and download them in CSV/PDF format.

---
""")

# Initialize NLTK
try:
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception as e:
    st.warning(f"NLTK initialization issue: {str(e)}")

# Import local modules
try:
    from resume_parser import parse_resume
    from job_matcher import get_resume_match_score
except ImportError as e:
    st.error(f"Failed to import local modules: {str(e)}")
    st.stop()

# Constants
SKILL_THRESHOLD = 0.85  # Similarity threshold for skill matching
MIN_WORD_COUNT = 100    # Minimum words for a decent resume

def match_label(score: float) -> str:
    """Categorize match score into quality labels"""
    if score >= 70:
        return "🟢 High"
    elif score >= 40:
        return "🟡 Medium"
    return "🔴 Low"

def analyze_resume_quality(data: Dict[str, Any], word_count: int) -> tuple:
    """Evaluate resume completeness and quality"""
    score = 0
    feedback = []
    
    # Check basic contact info
    required_fields = {
        'name': ("Missing Name", 10),
        'email': ("Missing Email", 10), 
        'phone': ("Missing Phone", 10),
        'skills': ("Missing Skills", 10)
    }
    
    for field, (msg, points) in required_fields.items():
        if data.get(field):
            score += points
        else:
            feedback.append(msg)
    
    # Evaluate length
    if word_count < MIN_WORD_COUNT:
        feedback.append(f"Too Short (<{MIN_WORD_COUNT} words)")
    elif word_count <= 250:
        score += 10
    else:
        score += 20
    
    # Check important sections
    sections = ["education", "experience", "skills", "projects"]
    raw = data.get('raw_text', '').lower()
    found_sections = [s for s in sections if s in raw]
    score += len(found_sections) * 10
    
    if missing := list(set(sections) - set(found_sections)):
        feedback.append(f"Missing Sections: {', '.join(missing)}")
    
    # Quality summary
    if score >= 90:
        summary = "✅ Excellent Resume"
    elif score >= 70:
        summary = "👍 Good Resume"
    elif score >= 50:
        summary = "⚠️ Needs Improvement"
    else:
        summary = "❌ Poor Resume"
        
    return score, f"{summary} | {'; '.join(feedback)}"

def generate_pdf(data: Dict[str, Any]) -> str:
    """Generate PDF report for a resume"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    try:
        pdf.cell(200, 10, txt=f"Resume Report: {data.get('Name','')}", ln=True, align='C')
    except Exception:
        pdf.cell(200, 10, txt="Resume Report", ln=True, align='C')
    
    for key, value in data.items():
        if key not in ["File", "Rank"]:
            try:
                text = f"{key}: {value}"
                pdf.multi_cell(0, 10, txt=text.encode('latin-1', 'replace').decode('latin-1'))
            except Exception:
                continue
                
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf.output(tmp_pdf.name)
        return tmp_pdf.name

def process_files(uploaded_resumes: List, uploaded_jd) -> Optional[pd.DataFrame]:
    """Main processing function"""
    if not uploaded_resumes or not uploaded_jd:
        st.warning("Please upload both resumes and a job description")
        return None
    
    try:
        jd_text = uploaded_jd.read().decode("utf-8")
    except Exception as e:
        st.error(f"Failed to read JD: {str(e)}")
        return None
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, resume_file in enumerate(uploaded_resumes, 1):
        status_text.text(f"Processing {idx}/{len(uploaded_resumes)}: {resume_file.name}")
        progress_bar.progress(idx/len(uploaded_resumes))
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(resume_file.read())
                tmp_path = tmp.name
        except Exception as e:
            st.error(f"Failed to save {resume_file.name}: {str(e)}")
            continue
            
        try:
            # Parse resume
            data = parse_resume(tmp_path)
            raw_text = data.get('raw_text', '')
            resume_skills = set(skill.lower() for skill in data.get('skills', []))
            
            # Get match scores
            match = get_resume_match_score(
                resume_data=data,
                jd_text=jd_text,
                resume_skills=resume_skills,
                jd_skills=resume_skills  # This will be processed in job_matcher
            )
            
            # Quality analysis
            quality_score, feedback = analyze_resume_quality(data, len(raw_text.split()))
            
            # Prepare results
            results.append({
                "File": resume_file.name,
                "Name": data.get('name'),
                "Email": data.get('email'),
                "Phone": data.get('phone'),
                "Skills": ', '.join(sorted(resume_skills)),
                "Matched Skills": ', '.join(match.get('matched_skills', [])),
                "Missing Skills": ', '.join(match.get('missing_skills', [])),
                "Matched Keywords": ', '.join(match.get('matched_keywords', [])),
                "Text Similarity (%)": match.get('similarity_score', 0),
                "Skill Match (%)": match.get('skill_score', 0),
                "Final Match (%)": match.get('final_score', 0),
                "Match Quality": match_label(match.get('final_score', 0)),
                "Resume Quality Score": quality_score,
                "Feedback Summary": feedback
            })
            
        except Exception as e:
            st.error(f"Error processing {resume_file.name}: {str(e)}")
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
    
    if not results:
        return None
        
    df = pd.DataFrame(results)
    df.sort_values("Final Match (%)", ascending=False, inplace=True)
    df["Rank"] = range(1, len(df)+1)
    return df

def display_results(df: pd.DataFrame):
    """Display and visualize results"""
    st.success(f"✅ Processed {len(df)} resumes successfully!")
    
    # Display dataframe
    try:
        styled = df.style.highlight_max(
            subset=["Final Match (%)", "Resume Quality Score"], 
            color='lightgreen'
        ).format({
            "Text Similarity (%)": "{:.1f}",
            "Skill Match (%)": "{:.1f}",
            "Final Match (%)": "{:.1f}",
            "Resume Quality Score": "{:.0f}"
        })
        st.dataframe(styled)
    except Exception:
        st.dataframe(df)
    
    # Visualizations
    with st.expander("📊 Visual Analysis"):
        col1, col2 = st.columns(2)
        with col1:
            try:
                fig, ax = plt.subplots()
                sns.histplot(df["Final Match (%)"], bins=10, kde=True, ax=ax)
                ax.set_title("Match Score Distribution")
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Plot error: {str(e)}")
        
        with col2:
            try:
                fig, ax = plt.subplots()
                df["Match Quality"].value_counts().plot(kind='bar', ax=ax)
                ax.set_title("Match Quality Distribution")
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Plot error: {str(e)}")
    
    # Download options
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Download All Results (CSV)",
        csv,
        "resume_matches.csv",
        "text/csv"
    )
    
    # PDF reports
    st.subheader("Individual PDF Reports")
    for _, row in df.iterrows():
        try:
            pdf_path = generate_pdf(row.to_dict())
            with open(pdf_path, "rb") as f:
                st.download_button(
                    f"📄 {row['Name']} Report",
                    f.read(),
                    f"{row['Name']}_report.pdf",
                    "application/pdf"
                )
            os.remove(pdf_path)
        except Exception as e:
            st.error(f"Failed to generate PDF for {row['Name']}: {str(e)}")

# Main UI
uploaded_resumes = st.file_uploader(
    "📄 Upload Resumes (PDF)", 
    type="pdf", 
    accept_multiple_files=True
)
uploaded_jd = st.file_uploader(
    "📋 Upload Job Description (TXT)", 
    type="txt"
)

if st.button("🔍 Analyze Resumes") and uploaded_resumes and uploaded_jd:
    with st.spinner("Processing resumes..."):
        start_time = time.time()
        df = process_files(uploaded_resumes, uploaded_jd)
        
        if df is not None:
            display_results(df)
            st.info(f"Completed in {time.time()-start_time:.1f} seconds")