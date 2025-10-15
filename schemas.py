from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ResumeBase(BaseModel):
    name: str = Field(..., example="Jane Doe")
    email: Optional[str] = Field(None, example="jane.doe@example.com")
    phone: Optional[str] = Field(None, example="+14155552671")
    skills: List[str] = Field(default=[], example=["Python", "FastAPI", "SQL"])
    experience: float = Field(..., example=5.5)
    education: List[str] = Field(default=[], example=["B.S. in Computer Science"])
    raw_text: str

class ResumeCreate(ResumeBase):
    filename: str

class ResumeResponse(ResumeBase):
    id: int
    filename: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobDescriptionBase(BaseModel):
    title: str = Field(..., example="Senior Python Developer")
    description: str = Field(..., example="Developing and maintaining web applications...")
    required_skills: List[str] = Field(..., example=["Python", "FastAPI", "PostgreSQL"])
    required_experience: float = Field(..., example=5.0)
    required_education: Optional[str] = Field(None, example="Bachelor's Degree")

class JobDescriptionCreate(JobDescriptionBase):
    pass

class JobDescriptionResponse(JobDescriptionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class MatchResultBase(BaseModel):
    match_score: float = Field(..., example=8.5)
    summary: str = Field(..., example="A strong candidate with relevant experience.")
    strengths: List[str] = Field(..., example=["Expert in Python", "5+ years of experience"])
    gaps: List[str] = Field(..., example=["Lacks experience with Kubernetes"])

class MatchResponse(MatchResultBase):
    resume: ResumeResponse
    job_description: JobDescriptionResponse

class MatchResultResponse(MatchResultBase):
    id: int
    resume_id: int
    job_description_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class BulkMatchRequest(BaseModel):
    resume_ids: List[int] = Field(..., example=[1, 2, 3])
    job_description_id: int = Field(..., example=1)

class BulkMatchResponse(BaseModel):
    results: List[MatchResponse]