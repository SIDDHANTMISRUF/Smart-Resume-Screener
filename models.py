from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    skills = Column(JSON)
    experience = Column(Float)
    education = Column(JSON)
    raw_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    required_skills = Column(JSON)
    required_experience = Column(Float)
    required_education = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class MatchResult(Base):
    __tablename__ = "match_results"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, index=True)
    job_description_id = Column(Integer, index=True)
    match_score = Column(Float)
    summary = Column(Text) # Changed from justification
    strengths = Column(JSON)
    gaps = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())