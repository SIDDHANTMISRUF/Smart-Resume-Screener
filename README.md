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

🏗️ System Architecture
The application follows a decoupled client-server architecture. The React frontend communicates with the FastAPI backend via a REST API. The backend handles all business logic, including PDF parsing, database interactions, and the hybrid matching process.

Code snippet

graph TD
    subgraph Browser
        A[React Frontend]
    end

    subgraph Server / Backend
        B[FastAPI Backend]
        C[Database - SQLite/PostgreSQL]
        D[PDF Parser - spaCy & Rules]
        E[Matching Engine]
        F[Groq API - LLM]
    end

    A -- REST API Calls --> B
    B -- Uploads PDF --> D
    D -- Returns Structured Data --> B
    B -- Stores/Retrieves Data --> C
    B -- Initiates Match --> E
    E -- Performs Rule-Based Analysis --> E
    E -- Sends Prompts --> F
    F -- Returns AI Analysis (JSON) --> E
    E -- Combines Scores --> B
    B -- Returns Final Match Results --> A
🧠 LLM Prompting Strategy
To ensure consistent and high-quality analysis from the AI, we use an advanced prompting technique involving a System Prompt and a User Prompt. This "few-shot" approach trains the model on the exact output format and quality we expect.

System Prompt
The system prompt establishes the LLM's persona, provides strict formatting rules, and includes a perfect example of the desired output. This dramatically improves the reliability of the JSON response.

Plaintext

You are an expert HR Technology Analyst. Your task is to evaluate a candidate's resume against a job description and provide a structured JSON analysis.

You MUST follow these rules:
1.  Your entire response must be a single, valid JSON object. Do not include any text before or after the JSON.
2.  Analyze the candidate based ONLY on the provided resume text. Do not invent skills or experience.
3.  The 'match_score' must be a float between 1.0 and 10.0.
4.  'summary', 'strengths', and 'gaps' must be concise, insightful, and directly related to the job requirements.
5.  If the candidate is a student or has low experience, focus on potential, projects, and academic alignment.

Here is a perfect example of your required output format:

{
  "match_score": 8.2,
  "summary": "Strong candidate with excellent alignment in core web technologies (React, Node.js) and cloud experience (AWS). Meets the required years of experience and possesses strong project management skills. Minor gap in PostgreSQL, but has related SQL experience making it a low risk.",
  "strengths": [
    "Exceeds requirement for React and Node.js proficiency.",
    "3 years of professional AWS experience aligns perfectly with job needs.",
    "Demonstrated leadership and agile methodology experience in past projects."
  ],
  "gaps": [
    "Lacks direct experience with PostgreSQL, a required skill.",
    "No mention of CI/CD tools like Jenkins or Terraform."
  ],
  "is_student": false
}
User Prompt
The user prompt provides the specific data for the current task, including resume snippets and job requirements, giving the model all the context it needs to perform the analysis.

Plaintext

Analyze the following data and generate the JSON response.

**CANDIDATE PROFILE**
- **Type**: This is an EXPERIENCED PROFESSIONAL profile. Evaluate against specific years of experience.
- **Experience (Years)**: 8.0
- **Skills**: Java, Spring Boot, Python, AWS, Kubernetes, Terraform, Microservices
- **Resume Snippet**: "SAMEER KHAN | Senior Cloud Architect... EXPERIENCE 2018 - Present Lead Software Architect, CloudNet Led the migration of monolithic applications to a microservices architecture on AWS using Kubernetes and Terraform. My total professional experience is now 8+ years..."

**JOB DESCRIPTION**
- **Title**: Senior Backend Engineer (Python)
- **Required Experience (Years)**: 5.0
- **Required Skills**: Python, Django, PostgreSQL, AWS, Docker, CI/CD, Microservices
- **Details**: "We are seeking a seasoned Senior Backend Engineer with a strong background in Python to lead the development of our core platform. You will design, build, and maintain scalable, high-performance microservices, manage our cloud infrastructure..."
🚀 Getting Started
Follow these instructions to set up and run the project locally.

Prerequisites
Python 3.8+

Node.js 16+ and npm

Git

1. Backend Setup (FastAPI)
Bash

# Clone the repository
git clone https://github.com/your-username/smart-resume-screener.git
cd smart-resume-screener/backend # Navigate to your backend directory

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Download the spaCy NLP model
python -m spacy download en_core_web_sm

# Create a .env file for your API key
touch .env
Add your Groq API key to the .env file:

GROQ_API_KEY="your_actual_groq_api_key_here"
2. Frontend Setup (React)
Open a new terminal for the frontend.

Bash

# Navigate to your frontend directory
cd ../frontend

# Install Node.js dependencies
npm install
3. Running the Application
Start the Backend Server:
In your backend terminal (with the virtual environment activated):

Bash

uvicorn main:app --reload
The API will be available at http://127.0.0.1:8000.

Start the Frontend Server:
In your frontend terminal:

Bash

npm start
The application will open in your browser at http://localhost:3000.

📜 API Endpoints
A brief overview of the main API endpoints:

POST /upload-resume/: Upload and parse a PDF resume.

GET /resumes/: Get a list of all resumes.

POST /job-descriptions/: Create a new job description.

GET /job-descriptions/: Get a list of all jobs.

POST /bulk-match/: Match multiple resumes to a job.

GET /match-results/: Get saved match results.

DELETE /reset-all-data/: (DANGER) Deletes all data in the database.

License
This project is licensed under the MIT License. See the LICENSE file for details.