🤖 Smart Resume Screener
An intelligent, full-stack application designed to automate the initial stages of recruitment. This tool uses a hybrid AI approach, combining a rule-based engine with a powerful Large Language Model (LLM) to parse candidate resumes, match them against job descriptions, and provide a detailed analysis with a match score.

Core Features

📄 Intelligent Resume Parsing: Upload PDF resumes and automatically extract key information like name, contact details, skills, and years of experience using an evidence-based parsing engine.

💼 Job Description Management: Create, view, and manage job descriptions with specific requirements for skills and experience.

🧠 Hybrid AI Matching: Utilizes both a fast, rule-based engine (TF-IDF for skills, direct experience comparison) and a sophisticated LLM (via Groq API) for nuanced, contextual analysis.

📊 Detailed Candidate Analysis: For each match, the system provides a score (1-10), a concise summary, and a list of specific strengths and gaps.

** Bulk Processing**: Match multiple candidates against a job description in a single operation.

Modern Web Interface: A clean, responsive user interface built with React for a seamless user experience.

RESTful API: A robust backend built with FastAPI and SQLAlchemy for efficient data management and scalability.


💻 Tech Stack

Frontend: React, Axios

Backend: Python, FastAPI

Database: SQLAlchemy, SQLite (easily configurable for PostgreSQL)

AI & NLP: spaCy, Scikit-learn, pdfplumber

LLM Provider: Groq (for high-speed Llama 3.1 inference)
