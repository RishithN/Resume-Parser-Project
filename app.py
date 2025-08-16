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

Match multiple resumes against a job description (job_description.txt)  
Get scores, matched/missing skills, and download results in CSV/PDF format.

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
    """Categorize match score"""
    if score >= 70: return "🟢 High"
    if score >= 40: return "🟡 Medium"
    return "🔴 Low"

def analyze_resume_quality(data: Dict[str, Any]) -> Tuple[int, str]:
    """Evaluate resume completeness"""
    score = 0
    feedback = []
    
    # Check basic info
    if data.get('name') and data['name'].lower() not in ["unknown", ""]:
        score += 10
    else:
        feedback.append("Missing Name")
    
    if data.get('email'): score += 10
    else: feedback.append("Missing Email")
    
    if data.get('phone'): score += 10
    else: feedback.append("Missing Phone")
    
    if data.get('skills'): score += 10
    else: feedback.append("Missing Skills")
    
    # Check length
    word_count = len(data.get('raw_text', '').split())
    if word_count < MIN_WORD_COUNT:
        feedback.append(f"Too Short (<{MIN_WORD_COUNT} words)")
    elif word_count <= 250: score += 10
    else: score += 20
    
    # Check sections
    sections = ["education", "experience", "skills", "projects"]
    found = [s for s in sections if s in data.get('raw_text', '').lower()]
    score += len(found) * 10
    if missing := list(set(sections) - set(found)):
        feedback.append(f"Missing: {', '.join(missing)}")
    
    # Quality summary
    if score >= 90: summary = "✅ Excellent"
    elif score >= 70: summary = "👍 Good"
    elif score >= 50: summary = "⚠️ Needs Work"
    else: summary = "❌ Poor"
    
    return score, f"{summary} | {'; '.join(feedback)}"

def generate_pdf(data: Dict[str, Any]) -> str:
    """Create PDF report for a resume"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Resume Analysis Report", ln=True, align='C')
    
    for key, value in data.items():
        if key not in ["File", "Rank"]:
            try:
                text = f"{key}: {value}"
                pdf.multi_cell(0, 10, txt=text.encode('latin-1', 'replace').decode('latin-1'))
            except:
                continue
                
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        return tmp.name

def load_jd_skills() -> Tuple[str, List[str]]:
    """Load job description and extract skills"""
    if not os.path.exists(JD_FILE):
        st.error(f"Job description file '{JD_FILE}' not found in project directory")
        st.stop()
    
    with open(JD_FILE, 'r', encoding='utf-8') as f:
        jd_text = f.read()
    
    return jd_text, extract_jd_skills(jd_text)

def main():
    """Main application flow"""
    # Load JD once at startup
    jd_text, jd_skills = load_jd_skills()
    
    st.sidebar.markdown("### Job Description Info")
    st.sidebar.text(f"Skills extracted: {len(jd_skills)}")
    if st.sidebar.button("View JD Skills"):
        st.sidebar.write(jd_skills)
    
    uploaded_resumes = st.file_uploader(
        "📄 Upload Resumes (PDF)", 
        type="pdf", 
        accept_multiple_files=True
    )
    
    if not uploaded_resumes:
        st.warning("Please upload resume PDFs")
        return
    
    if st.button("🔍 Analyze Resumes"):
        start_time = time.time()
        results = []
        
        with st.spinner(f"Processing {len(uploaded_resumes)} resumes..."):
            for resume_file in uploaded_resumes:
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(resume_file.read())
                        tmp_path = tmp.name
                    
                    # Parse resume
                    data = parse_resume(tmp_path)
                    resume_skills = [s.lower() for s in data.get('skills', [])]
                    
                    # Calculate matches
                    match = get_resume_match_score(
                        resume_data=data,
                        jd_text=jd_text,
                        resume_skills=resume_skills,
                        jd_skills=jd_skills
                    )
                    
                    # Quality analysis
                    quality_score, feedback = analyze_resume_quality(data)
                    
                    # Store results
                    results.append({
                        "File": resume_file.name,
                        "Name": data.get('name'),
                        "Email": data.get('email'),
                        "Phone": data.get('phone'),
                        "Skills": ', '.join(sorted(resume_skills)),
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
        
        if not results:
            st.error("No results generated")
            return
        
        # Create and display results dataframe
        df = pd.DataFrame(results)
        df.sort_values("Final Score", ascending=False, inplace=True)
        df.insert(0, "Rank", range(1, len(df)+1))
        
        st.success(f"✅ Analysis completed in {time.time()-start_time:.1f} seconds")
        st.dataframe(df.style.format({
            "Skill Match %": "{:.1f}%",
            "Final Score": "{:.1f}%"
        }))
        
        # Visualizations
        with st.expander("📊 Visual Analysis"):
            fig, ax = plt.subplots(1, 2, figsize=(12, 4))
            
            # Score distribution
            sns.histplot(df["Final Score"], bins=10, kde=True, ax=ax[0])
            ax[0].set_title("Match Score Distribution")
            
            # Quality distribution
            df["Match Quality"].value_counts().plot(kind='bar', ax=ax[1])
            ax[1].set_title("Match Quality")
            
            st.pyplot(fig)
        
        # Download options
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "💾 Download CSV",
            csv,
            "resume_analysis_results.csv",
            "text/csv"
        )
        
        # Individual PDF reports
        st.subheader("📄 Individual Reports")
        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                with st.expander(f"Report #{row['Rank']}: {row['Name']}"):
                    st.write(f"**Match Score:** {row['Final Score']:.1f}%")
                    st.write(f"**Skills Match:** {row['Skill Match %']:.1f}%")
                    
                    if st.button(f"Download PDF", key=f"pdf_{idx}"):
                        pdf_path = generate_pdf(row.to_dict())
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                "⬇️ Download",
                                f.read(),
                                f"{row['Name']}_report.pdf",
                                "application/pdf"
                            )
                        os.remove(pdf_path)

if __name__ == "__main__":
    main()