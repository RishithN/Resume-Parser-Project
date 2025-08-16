import streamlit as st
import os
import tempfile
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import re

st.set_page_config(page_title="📄 Resume Matcher", layout="centered", initial_sidebar_state="collapsed")

st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
if os.path.exists(logo_path):
    st.image(logo_path, width=150)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
# 📄 Resume Parser & JD Matcher

Match multiple resumes against a job description using Python NLP.  
Get scores, preview results, and download them in CSV format.

---
""")

st.text("Startup: beginning environment checks...")

# --- NLTK Setup ---
import nltk
nltk_data_path = os.path.join(os.path.expanduser("~"), "nltk_data")
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)
for pkg in ["punkt", "stopwords", "wordnet"]:
    try:
        if pkg == "punkt":
            nltk.data.find("tokenizers/punkt")
        else:
            nltk.data.find(f"corpora/{pkg}")
    except LookupError:
        try:
            nltk.download(pkg, download_dir=nltk_data_path)
        except Exception:
            pass

st.text("NLTK data ensured (if possible).")

try:
    from resume_parser import parse_resume
    from job_matcher import get_resume_match_score
    st.text("Imported local modules: resume_parser, job_matcher")
except Exception as e:
    st.error("Error importing local modules.")
    st.exception(e)
    st.stop()

uploaded_resumes = st.file_uploader("📄 Upload PDF Resumes", type="pdf", accept_multiple_files=True)
uploaded_jd = st.file_uploader("📋 Upload Job Description (.txt)", type="txt")

# ----------------------------
# Helper Functions
# ----------------------------
def match_label(score):
    if score >= 70:
        return "🟢 High"
    elif score >= 40:
        return "🟡 Medium"
    else:
        return "🔴 Low"

def analyze_resume_quality(data, word_count):
    score = 0
    feedback = []
    if data.get('name') and data.get('name').lower() not in ["unknown", ""]:
        score += 10
    else:
        feedback.append("Missing Name")
    if data.get('email'):
        score += 10
    else:
        feedback.append("Missing Email")
    if data.get('phone'):
        score += 10
    else:
        feedback.append("Missing Phone")
    if data.get('skills'):
        score += 10
    else:
        feedback.append("Missing Skills")
    if word_count < 100:
        feedback.append("Too Short (<100 words)")
    elif word_count <= 250:
        score += 10
    else:
        score += 20
    sections = ["education", "experience", "skills", "projects"]
    raw = data.get('raw_text', '').lower()
    found_sections = [s for s in sections if s in raw]
    score += len(found_sections) * 10
    missing_sections = list(set(sections) - set(found_sections))
    if missing_sections:
        feedback.append("Missing Sections: " + ", ".join(missing_sections))
    if score >= 90:
        summary = "✅ Excellent Resume"
    elif score >= 70:
        summary = "👍 Good Resume"
    elif score >= 50:
        summary = "⚠️ Needs Improvement"
    else:
        summary = "❌ Poor Resume"
    return score, summary + " | " + "; ".join(feedback)

def generate_pdf(data):
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
                try:
                    pdf.multi_cell(0, 10, txt=str(key) + ": [unprintable]")
                except Exception:
                    continue
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf.output(tmp_pdf.name)
        return tmp_pdf.name

# ----------------------------
# Skill Cleaning & Extraction
# ----------------------------
def clean_skill(skill: str) -> str:
    """Normalize a skill string (lowercase, strip, remove punctuation)."""
    if not skill:
        return ""
    skill = skill.lower().strip()
    skill = re.sub(r"[^\w\s\+\#]", "", skill)  # allow alphanum, +, #
    return skill

def extract_skills_from_text(text: str, known_skills: list) -> list:
    """Extract skills by matching known skills inside JD/resume text."""
    text = text.lower()
    found = []
    for skill in known_skills:
        if skill.lower() in text:
            found.append(skill.lower())
    return list(set(found))

# Example dictionary of skills (extend as needed)
KNOWN_SKILLS = [
    "python", "java", "c++", "c#", "sql", "excel", "power bi",
    "machine learning", "deep learning", "tensorflow", "keras", "pytorch",
    "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn",
    "data analysis", "data visualization", "nlp", "project management",
    "communication", "leadership"
]

# ----------------------------
# Main Logic
# ----------------------------
if uploaded_resumes and uploaded_jd:
    if st.button("🔍 Match Resumes Now"):
        start_time = time.time()
        try:
            jd_text = uploaded_jd.read().decode("utf-8")
            extracted_jd_skills = extract_skills_from_text(jd_text, KNOWN_SKILLS)
        except Exception:
            jd_text = ""
            extracted_jd_skills = []

        results = []
        st.info(f"Matching {len(uploaded_resumes)} resume(s)...")
        with st.spinner("🔄 Processing..."):
            for idx, resume_file in enumerate(uploaded_resumes, start=1):
                st.text(f"Processing file {idx}/{len(uploaded_resumes)}: {resume_file.name}")
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(resume_file.read())
                        tmp_path = tmp.name
                except Exception as e:
                    st.error(f"Failed to save uploaded file {resume_file.name}")
                    st.exception(e)
                    continue

                # --- Parse Resume ---
                try:
                    data = parse_resume(tmp_path)
                except Exception as e:
                    data = {"name":"Unknown","email":None,"phone":None,"skills":[],"raw_text":""}
                    st.error(f"parse_resume failed for {resume_file.name}")
                    st.exception(e)

                raw_text = data.get('raw_text', '')
                extracted_resume_skills = [clean_skill(s) for s in data.get('skills', []) if s]

                # --- Compute Matched / Missing Skills ---
                jd_skills_set = set(extracted_jd_skills)
                resume_skills_set = set(extracted_resume_skills)
                matched_skills = sorted(list(jd_skills_set & resume_skills_set))
                missing_skills = sorted(list(jd_skills_set - resume_skills_set))

                # Resume Score (% of JD skills matched)
                if jd_skills_set:
                    resume_score = round(len(matched_skills) / len(jd_skills_set) * 100, 2)
                else:
                    resume_score = 0

                # --- Keyword / similarity score (optional) ---
                try:
                    match = get_resume_match_score(resume_text=raw_text,
                                                   resume_skills=extracted_resume_skills,
                                                   jd_text=jd_text)
                except Exception as e:
                    st.error(f"get_resume_match_score failed for {resume_file.name}")
                    st.exception(e)
                    match = {"similarity_score":0,
                             "skill_score":resume_score,
                             "final_score":resume_score,
                             "matched_skills":matched_skills,
                             "missing_skills":missing_skills,
                             "matched_keywords":[]}

                # --- Resume Quality ---
                quality_score, feedback_summary = analyze_resume_quality(data, len(raw_text.split()))

                # --- Append Results ---
                results.append({
                    "File": resume_file.name,
                    "Name": data.get('name'),
                    "Email": data.get('email'),
                    "Phone": data.get('phone'),
                    "Skills": ', '.join(extracted_resume_skills),
                    "Matched Skills": ', '.join(matched_skills),
                    "Missing Skills": ', '.join(missing_skills),
                    "Matched Keywords": ', '.join(match.get('matched_keywords', [])),
                    "Text Similarity (%)": match.get('similarity_score', 0),
                    "Skill Match (%)": match.get('skill_score', resume_score),
                    "Final Match (%)": match.get('final_score', resume_score),
                    "Match Quality": match_label(match.get('final_score', resume_score)),
                    "Resume Quality Score": quality_score,
                    "Feedback Summary": feedback_summary
                })

                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

        # --- Display Results ---
        df = pd.DataFrame(results)
        if df.empty:
            st.warning("No results to display.")
        else:
            df.sort_values(by="Final Match (%)", ascending=False, inplace=True)
            df["Rank"] = range(1, len(df) + 1)
            df = df[["Rank", "File", "Name", "Email", "Phone", "Skills",
                     "Matched Skills", "Missing Skills", "Matched Keywords",
                     "Text Similarity (%)", "Skill Match (%)", "Final Match (%)",
                     "Match Quality", "Resume Quality Score", "Feedback Summary"]]
            st.success("✅ Matching complete! Here are the results:")
            try:
                styled = df.style.highlight_max(axis=0, subset=["Final Match (%)", "Resume Quality Score"], color='lightgreen').format({
                    "Text Similarity (%)": "{:.2f}",
                    "Skill Match (%)": "{:.2f}",
                    "Final Match (%)": "{:.2f}",
                    "Resume Quality Score": "{:.0f}"
                })
                st.dataframe(styled)
            except Exception:
                st.dataframe(df)

            # --- Visual Analysis ---
            with st.expander("📊 Visual Analysis"):
                col1, col2 = st.columns(2)
                with col1:
                    try:
                        fig1, ax1 = plt.subplots()
                        ax1.hist(df["Final Match (%)"], bins=10, color="skyblue", edgecolor="black")
                        ax1.set_title("📈 Final Match Score Distribution")
                        ax1.set_xlabel("Match Score (%)")
                        ax1.set_ylabel("Number of Candidates")
                        st.pyplot(fig1)
                    except Exception as e:
                        st.error("Error plotting histogram")
                        st.exception(e)
                with col2:
                    try:
                        fig2, ax2 = plt.subplots()
                        quality_counts = df["Match Quality"].value_counts()
                        ax2.bar(quality_counts.index, quality_counts.values, color="orange")
                        ax2.set_title("📊 Match Quality (High / Med / Low)")
                        ax2.set_ylabel("Count")
                        st.pyplot(fig2)
                    except Exception as e:
                        st.error("Error plotting match quality")
                        st.exception(e)
                try:
                    all_skills = list(set(skill for skills in df["Skills"] for skill in skills.split(", ") if skill.strip()))
                    heatmap_data = []
                    for i, row in df.iterrows():
                        row_data = [1 if skill in row["Matched Skills"].split(", ") else 0 for skill in all_skills]
                        heatmap_data.append(row_data)
                    heatmap_df = pd.DataFrame(heatmap_data, columns=all_skills, index=df["Name"])
                    fig3, ax3 = plt.subplots(figsize=(12, max(2, len(df) * 0.5)))
                    sns.heatmap(heatmap_df, cmap="Greens", cbar=True, linewidths=0.5, linecolor="gray", ax=ax3)
                    ax3.set_title("Skill Match Heatmap")
                    st.pyplot(fig3)
                except Exception as e:
                    st.error("Error creating heatmap")
                    st.exception(e)

            # --- Download CSV ---
            csv_all = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download All Results (CSV)", csv_all, "all_results.csv", "text/csv", use_container_width=True)

            shortlisted_df = df[df["Final Match (%)"] >= 55]
            if not shortlisted_df.empty:
                csv_shortlist = shortlisted_df.to_csv(index=False).encode("utf-8")
                st.download_button("✅ Download Shortlisted Only (≥ 55%)", csv_shortlist, "shortlisted_candidates.csv", "text/csv", use_container_width=True)

            # --- Download PDF ---
            st.subheader("📁 Download PDF Reports")
            for i, row in df.iterrows():
                try:
                    pdf_path = generate_pdf(row)
                    with open(pdf_path, "rb") as f:
                        st.download_button(f"⬇️ {row['Name']} Resume Report", f.read(), file_name=f"{row['Name']}_report.pdf", use_container_width=True)
                    os.remove(pdf_path)
                except Exception as e:
                    st.error(f"Failed to generate/download PDF for {row.get('Name')}")
                    st.exception(e)

            st.markdown("---")
            st.markdown("🧠 Powered by Python, scikit-learn, and Streamlit")
        elapsed = time.time() - start_time
        st.text(f"Processing completed in {elapsed:.2f} seconds")
else:
    st.warning("👆 Please upload both resumes and a job description file to begin.")
