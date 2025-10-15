from sqlalchemy.orm import Session
from . import models, schemas
from typing import List

# Resume CRUD
def get_resume(db: Session, resume_id: int):
    return db.query(models.Resume).filter(models.Resume.id == resume_id).first()

def get_resumes(db: Session, skip: int = 0, limit: int = 100) -> List[models.Resume]:
    return db.query(models.Resume).offset(skip).limit(limit).all()

def create_resume(db: Session, resume: schemas.ResumeCreate) -> models.Resume:
    db_resume = models.Resume(**resume.dict())
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

# Job Description CRUD
def get_job_description(db: Session, job_id: int):
    return db.query(models.JobDescription).filter(models.JobDescription.id == job_id).first()

def get_job_descriptions(db: Session, skip: int = 0, limit: int = 100) -> List[models.JobDescription]:
    return db.query(models.JobDescription).offset(skip).limit(limit).all()

def create_job_description(db: Session, job: schemas.JobDescriptionCreate) -> models.JobDescription:
    db_job = models.JobDescription(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

# Match Result CRUD
def create_match_result(db: Session, result: dict) -> models.MatchResult:
    db_result = models.MatchResult(**result)
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def get_match_results_by_job(db: Session, job_id: int) -> List[models.MatchResult]:
    return db.query(models.MatchResult).filter(models.MatchResult.job_description_id == job_id).all()