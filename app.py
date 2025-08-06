import streamlit as st
import pandas as pd
import tempfile
import os
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import re
from resume_parser import parse_resume
from job_matcher import get_resume_match_score

st.set_page_config(
    page_title="📄 Resume Matcher",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image("logo.png", use_container_width=False, width=150)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
# 📄 Resume Parser & JD Matcher

Match multiple resumes against a job description using Python NLP.  
Get scores, preview results, and download them in CSV format.

---
""")

uploaded_resumes = st.file_uploader("📤 Upload PDF Resumes", type="pdf", accept_multiple_files=True)
uploaded_jd = st.file_uploader("📋 Upload Job Description (.txt)", type="txt")

def match_label(score):
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"

def analyze_resume_quality(data, word_count):
    score = 0
    feedback = []
    if data['name'] and data['name'].lower() not in ["unknown", ""]:
        score += 10
    else:
        feedback.append("Missing Name")
    if data['email']:
        score += 10
    else:
        feedback.append("Missing Email")
    if data['phone']:
        score += 10
    else:
        feedback.append("Missing Phone")
    if data['skills']:
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
    found_sections = [s for s in sections if s in data['raw_text'].lower()]
    score += len(found_sections) * 10
    missing_sections = list(set(sections) - set(found_sections))
    if missing_sections:
        feedback.append("Missing Sections: " + ", ".join(missing_sections))
    if score >= 90:
        summary = "Excellent Resume"
    elif score >= 70:
        summary = "Good Resume"
    elif score >= 50:
        summary = "Needs Improvement"
    else:
        summary = "Poor Resume"
    return score, summary + " | " + "; ".join(feedback)

def remove_emojis(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=remove_emojis(f"Resume Report: {data['Name']}"), ln=True, align='C')
    for key, value in data.items():
        if key not in ["File", "Rank"]:
            text = remove_emojis(f"{key}: {value}")
            pdf.multi_cell(0, 10, txt=text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf.output(tmp_pdf.name)
        return tmp_pdf.name

if uploaded_resumes and uploaded_jd:
    if st.button("🔍 Match Resumes Now"):
        jd_text = uploaded_jd.read().decode("utf-8")
        results = []
        st.info(f"Matching {len(uploaded_resumes)} resume(s)...")
        with st.spinner("🔄 Processing..."):
            for resume_file in uploaded_resumes:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(resume_file.read())
                    tmp_path = tmp.name
                data = parse_resume(tmp_path)
                raw_text = data.get('raw_text', '')
                match = get_resume_match_score(resume_text=raw_text, resume_skills=data['skills'], jd_text=jd_text)
                os.remove(tmp_path)
                quality_score, feedback_summary = analyze_resume_quality(data, len(raw_text.split()))
                results.append({
                    "File": resume_file.name,
                    "Name": data['name'],
                    "Email": data['email'],
                    "Phone": data['phone'],
                    "Skills": ', '.join(data['skills']),
                    "Matched Skills": ', '.join(match['matched_skills']),
                    "Missing Skills": ', '.join(match['missing_skills']),
                    "Matched Keywords": ', '.join(match['matched_keywords']),
                    "Text Similarity (%)": match['similarity_score'],
                    "Skill Match (%)": match['skill_score'],
                    "Final Match (%)": match['final_score'],
                    "Match Quality": match_label(match['final_score']),
                    "Resume Quality Score": quality_score,
                    "Feedback Summary": feedback_summary
                })
        df = pd.DataFrame(results)
        df.sort_values(by="Final Match (%)", ascending=False, inplace=True)
        df["Rank"] = range(1, len(df) + 1)
        df = df[["Rank", "File", "Name", "Email", "Phone", "Skills",
                 "Matched Skills", "Missing Skills", "Matched Keywords",
                 "Text Similarity (%)", "Skill Match (%)", "Final Match (%)",
                 "Match Quality", "Resume Quality Score", "Feedback Summary"]]
        st.success("✅ Matching complete! Here are the results:")
        st.dataframe(df)
        with st.expander("📊 Visual Analysis"):
            col1, col2 = st.columns(2)
            with col1:
                fig1, ax1 = plt.subplots()
                ax1.hist(df["Final Match (%)"], bins=10, color="skyblue", edgecolor="black")
                ax1.set_title("📈 Final Match Score Distribution")
                st.pyplot(fig1)
            with col2:
                fig2, ax2 = plt.subplots()
                quality_counts = df["Match Quality"].value_counts()
                ax2.bar(quality_counts.index, quality_counts.values, color="orange")
                ax2.set_title("📊 Match Quality (High / Med / Low)")
                st.pyplot(fig2)
            all_skills = list(set(skill for skills in df["Skills"] for skill in skills.split(", ")))
            heatmap_data = []
            for i, row in df.iterrows():
                row_data = [1 if skill in row["Matched Skills"].split(", ") else 0 for skill in all_skills]
                heatmap_data.append(row_data)
            heatmap_df = pd.DataFrame(heatmap_data, columns=all_skills, index=df["Name"])
            fig3, ax3 = plt.subplots(figsize=(12, len(df) * 0.5))
            sns.heatmap(heatmap_df, cmap="Greens", cbar=True, linewidths=0.5, linecolor="gray", ax=ax3)
            ax3.set_title("Skill Match Heatmap")
            st.pyplot(fig3)
        csv_all = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download All Results (CSV)", csv_all, "all_results.csv", "text/csv", use_container_width=True)
        shortlisted_df = df[df["Final Match (%)"] >= 55]
        if not shortlisted_df.empty:
            csv_shortlist = shortlisted_df.to_csv(index=False).encode("utf-8")
            st.download_button("✅ Download Shortlisted Only (≥ 55%)", csv_shortlist, "shortlisted_candidates.csv", "text/csv", use_container_width=True)
        st.subheader("📚 Download PDF Reports")
        for i, row in df.iterrows():
            pdf_path = generate_pdf(row)
            with open(pdf_path, "rb") as f:
                st.download_button(f"⬇️ {row['Name']} Resume Report", f.read(), file_name=f"{row['Name']}_report.pdf", use_container_width=True)
            os.remove(pdf_path)
        st.markdown("---")
        st.markdown("🧠 Powered by Python, spaCy, scikit-learn, and Streamlit")
else:
    st.warning("👇 Please upload both resumes and a job description file to begin.")
