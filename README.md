Resume Parser with JD Matching & Candidate Ranking

A web-based AI-powered Resume Parser that automates resume parsing, job description (JD) matching, candidate ranking, and shortlisting.
Built with Streamlit, NLP, and Machine Learning, this tool helps recruiters and hiring managers quickly identify the best-fit candidates for any job role.

🚀 Features

✔ Resume Parsing – Extracts key details such as:

Candidate Name

Email

Phone Number

Skills

✔ Job Description (JD) Matching –

TF-IDF-based text similarity for JD vs Resume matching

Keyword & skills-based comparison

✔ Candidate Ranking & Auto-Shortlisting –

Calculates a Match Score (%)

Labels match quality (High / Medium / Low)

Automatically ranks candidates

✔ Detailed Match Breakdown –

Matched Skills

Missing Skills

Keyword matches

✔ Resume Quality Analyzer –

Detects missing sections (Skills, Experience, Education, Projects)

Provides improvement suggestions

✔ Batch Resume Processing –

Upload multiple resumes (PDF format)

Compare all candidates against a single JD

✔ Data Export & Reporting –

Export results as CSV

Download PDF Report of candidates

✔ Visual Insights –

Match distribution charts

Interactive dashboards via Streamlit

✔ Notifications (Future Scope) –

Email shortlisted candidates via SMTP

🛠 Tech Stack

Python – Core programming language

Streamlit – Interactive web app UI

scikit-learn – TF-IDF & ML algorithms

NLTK / spaCy – NLP preprocessing & entity extraction

PyPDF2 – Resume PDF text extraction

Pandas – Data handling & ranking

Matplotlib / Seaborn – Charts & data visualization

📂 Project Structure
Resume-Parser-Project/
│── app.py                # Streamlit main application  
│── requirements.txt       # Dependencies  
│── logo.png               # App branding/logo  
│── resumes/               # Folder for sample resumes (PDFs)  
│── job_description.txt    # Example job description  
│── utils/                 # Helper functions (NLP, parsing, reports)  
│── output/                # Exported CSVs and PDF reports  
│── README.md              # Project documentation  

⚡ How to Run Locally

Clone Repository

git clone https://github.com/your-username/resume-parser-project.git
cd resume-parser-project


Install Requirements

pip install -r requirements.txt


Run the App

streamlit run app.py

📊 Sample Workflow

Upload multiple resumes (PDF format)

Upload a Job Description (TXT format)

App parses resumes → extracts data

TF-IDF + skill comparison → calculates match scores

Candidates are ranked with High / Medium / Low match labels

Export CSV / PDF reports

📈 Example Output

Candidate Ranking Table with Match Score (%)

Matched vs Missing Skills Breakdown

Match Distribution Chart

Resume Quality Report

🔮 Future Enhancements

Resume classification by job role

LinkedIn/Indeed API integration for automated JD fetching

AI-based scoring using embeddings (BERT / OpenAI models)

Advanced reporting dashboards

👨‍💻 Author

Rishith N
💼 Aspiring Data Analyst | AI Product Enthusiast | BTech CSE (Specialization in Data Analytics)

✨ With this project, resume screening & shortlisting becomes 10x faster, smarter, and more reliable.