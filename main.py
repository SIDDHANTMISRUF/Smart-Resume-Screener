from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, delete
import os
import shutil
from typing import List

from .database import get_db, create_tables
from .models import Resume, JobDescription, MatchResult
from .schemas import (
    ResumeResponse, JobDescriptionCreate, JobDescriptionResponse,
    MatchResponse, BulkMatchRequest, BulkMatchResponse, MatchResultResponse
)
from .pdf_parser import ResumeParser
from .matching_engine import MatchingEngine

# Create database tables on startup
create_tables()

app = FastAPI(
    title="Smart Resume Screener API",
    version="2.0.0",
    description="An advanced API for parsing resumes and matching them with job descriptions using a hybrid rule-based and LLM approach.",
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (singletons for the app's lifecycle)
parser = ResumeParser()
matching_engine = MatchingEngine()

# Create a directory for temporary file uploads
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    print("API starting up. Services initialized.")

@app.get("/", tags=["General"])
def read_root():
    """Root endpoint providing basic API information."""
    return {"message": "Welcome to the Smart Resume Screener API", "version": "2.0.0"}

@app.post("/upload-resume/", response_model=ResumeResponse, tags=["Resumes"])
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a resume PDF, parse it, and save the extracted data to the database."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Prevent duplicate filenames
    existing_resume = db.query(Resume).filter(Resume.filename == file.filename).first()
    if existing_resume:
        raise HTTPException(
            status_code=409,
            detail=f"A resume with the filename '{file.filename}' already exists."
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        # Save the uploaded file temporarily
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse the resume using the advanced parser
        parsed_data = parser.parse_resume(file_path)
        if parsed_data.get('name') == 'Parsing Failed':
             raise HTTPException(status_code=500, detail="Failed to extract text or parse the resume.")
        
        # Create a new resume record in the database
        resume = Resume(
            filename=file.filename,
            **parsed_data
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        return resume
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the resume: {str(e)}")
    
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/resumes/", response_model=List[ResumeResponse], tags=["Resumes"])
def get_all_resumes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a list of all parsed resumes from the database."""
    resumes = db.query(Resume).order_by(Resume.created_at.desc()).offset(skip).limit(limit).all()
    return resumes

@app.post("/job-descriptions/", response_model=JobDescriptionResponse, tags=["Jobs"])
def create_job_description(job: JobDescriptionCreate, db: Session = Depends(get_db)):
    """Create a new job description and save it to the database."""
    db_job = JobDescription(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.get("/job-descriptions/", response_model=List[JobDescriptionResponse], tags=["Jobs"])
def get_all_job_descriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a list of all job descriptions from the database."""
    jobs = db.query(JobDescription).order_by(JobDescription.created_at.desc()).offset(skip).limit(limit).all()
    return jobs

@app.post("/bulk-match/", response_model=BulkMatchResponse, tags=["Matching"])
def bulk_match_resumes(bulk_request: BulkMatchRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Match multiple resumes against a single job description."""
    job = db.query(JobDescription).filter(JobDescription.id == bulk_request.job_description_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job Description not found.")
    
    resumes_to_match = db.query(Resume).filter(Resume.id.in_(bulk_request.resume_ids)).all()
    if not resumes_to_match:
        raise HTTPException(status_code=404, detail="None of the provided resume IDs were found.")

    # Perform matching
    match_results = matching_engine.bulk_match(resumes_to_match, job)
    
    # Use background tasks to save results to DB without blocking the HTTP response
    background_tasks.add_task(save_match_results, match_results, db)
    
    # Format the response to include nested resume and job data
    response_results = []
    for result in match_results:
        resume_data = next((r for r in resumes_to_match if r.id == result['resume_id']), None)
        if resume_data:
            response_results.append(
                MatchResponse(
                    resume=resume_data,
                    job_description=job,
                    **result
                )
            )

    return BulkMatchResponse(results=response_results)

def save_match_results(results: List[dict], db: Session):
    """Helper function to save match results in the background."""
    match_records = []
    for result in results:
        match_records.append(MatchResult(**result))
    
    db.add_all(match_records)
    db.commit()
    print(f"✅ Successfully saved {len(match_records)} match results to the database.")

@app.get("/match-results/", response_model=List[MatchResultResponse], tags=["Matching"])
def get_match_results(job_id: int = None, db: Session = Depends(get_db)):
    """Retrieve match results, optionally filtered by job ID."""
    query = db.query(MatchResult)
    if job_id:
        query = query.filter(MatchResult.job_description_id == job_id)
    
    results = query.order_by(MatchResult.created_at.desc()).all()
    return results

@app.delete("/reset-all-data/", tags=["Admin"])
def reset_all_data(db: Session = Depends(get_db)):
    """
    DANGER ZONE: Deletes ALL data from resumes, jobs, and matches tables.
    This is irreversible.
    """
    try:
        db.execute(delete(MatchResult))
        db.execute(delete(JobDescription))
        db.execute(delete(Resume))
        
        # For SQLite, reset auto-incrementing counters
        if db.bind.dialect.name == "sqlite":
            db.execute(text("DELETE FROM sqlite_sequence;"))

        db.commit()
        return JSONResponse(
            status_code=200,
            content={"message": "✅ All data has been successfully reset."}
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error resetting data: {str(e)}")