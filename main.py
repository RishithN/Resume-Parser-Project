import os
import pandas as pd
from resume_parser import parse_resume
from job_matcher import read_job_description, get_resume_match_score

if __name__ == "__main__":
    resume_folder = "sample_data"
    jd_path = os.path.join(resume_folder, "jd.txt")
    jd_text = read_job_description(jd_path)

    results = []

    for filename in os.listdir(resume_folder):
        if filename.endswith(".pdf"):
            resume_path = os.path.join(resume_folder, filename)
            resume_data = parse_resume(resume_path)

            match_result = get_resume_match_score(
                resume_text=resume_data['name'] + ' ' + resume_data['email'] + ' ' +
                            resume_data['phone'] + ' ' + ' '.join(resume_data['skills']),
                resume_skills=resume_data['skills'],
                jd_text=jd_text
            )

            print(f"--- {filename} ---")
            print(f"Name               : {resume_data['name']}")
            print(f"Email              : {resume_data['email']}")
            print(f"Phone              : {resume_data['phone']}")
            print(f"Skills             : {', '.join(resume_data['skills'])}")
            print(f"Similarity Score   : {match_result['similarity_score']}%")
            print(f"Skill Match Score  : {match_result['skill_score']}%")
            print(f"Final Match Score  : {match_result['final_score']}%\n")

            results.append({
                "File": filename,
                "Name": resume_data['name'],
                "Email": resume_data['email'],
                "Phone": resume_data['phone'],
                "Skills": ', '.join(resume_data['skills']),
                "Text Similarity (%)": match_result['similarity_score'],
                "Skill Match (%)": match_result['skill_score'],
                "Final Match (%)": match_result['final_score']
            })

    df = pd.DataFrame(results)
    df.to_csv("results.csv", index=False)
    print("✅ Results saved to 'results.csv'")
