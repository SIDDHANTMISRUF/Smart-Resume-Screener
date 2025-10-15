from typing import Dict, List
from .llm_service import LLMService
from .models import Resume, JobDescription
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MatchingEngine:
    def __init__(self):
        self.llm_service = LLMService()
    
    def calculate_skill_score(self, resume_skills: List[str], job_skills: List[str]) -> float:
        """Calculate skill similarity using TF-IDF and cosine similarity."""
        if not resume_skills or not job_skills:
            return 0.0
        
        resume_text = ' '.join(skill.lower() for skill in resume_skills)
        job_text = ' '.join(skill.lower() for skill in job_skills)
        
        try:
            vectorizer = TfidfVectorizer().fit_transform([resume_text, job_text])
            vectors = vectorizer.toarray()
            similarity = cosine_similarity(vectors)
            return float(similarity[0][1])
        except Exception:
            # Fallback to simple overlap
            resume_set = set(s.lower() for s in resume_skills)
            job_set = set(s.lower() for s in job_skills)
            return len(resume_set.intersection(job_set)) / len(job_set)

    def calculate_experience_score(self, resume_exp: float, job_exp: float) -> float:
        """Calculate experience match score."""
        if job_exp <= 0: return 1.0
        if resume_exp <= 0: return 0.0
        return min(1.0, resume_exp / job_exp)
    
    def hybrid_match(self, resume: Resume, job: JobDescription) -> Dict:
        """Perform hybrid matching (rule-based + LLM) for a single resume."""
        
        # 1. Rule-based scoring (serves as a baseline and input for the final score)
        skill_score = self.calculate_skill_score(resume.skills, job.required_skills)
        exp_score = self.calculate_experience_score(resume.experience, job.required_experience)
        rule_based_score = (skill_score * 0.7) + (exp_score * 0.3)
        
        # 2. LLM-based analysis
        try:
            llm_result = self.llm_service.match_resume_job(resume.dict(), job.dict())
            llm_score = llm_result['match_score'] / 10.0  # Normalize to 0-1 scale
            
            # 3. Combine scores: 60% LLM, 40% rule-based
            final_score = (llm_score * 0.6) + (rule_based_score * 0.4)
            
            result = {
                "match_score": round(final_score * 10, 1),
                **llm_result  # Unpack summary, strengths, gaps, is_student
            }
            
        except Exception as e:
            print(f"❌ LLM matching failed, falling back to rule-based only: {e}")
            # Fallback to a response based purely on rules
            result = {
                "match_score": round(rule_based_score * 10, 1),
                "summary": "AI analysis failed. This result is based on a keyword and experience match only.",
                "strengths": [f"Skill match score: {skill_score:.2f}", f"Experience match score: {exp_score:.2f}"],
                "gaps": ["Detailed AI analysis is unavailable."],
                "is_student": resume.experience < 2
            }
        
        return result

    def bulk_match(self, resumes: List[Resume], job: JobDescription) -> List[Dict]:
        """Match multiple resumes efficiently."""
        results = []
        for resume in resumes:
            try:
                match_result = self.hybrid_match(resume, job)
                
                # Prepare result for database insertion
                db_result = {
                    'resume_id': resume.id,
                    'job_description_id': job.id,
                    'match_score': match_result['match_score'],
                    'summary': match_result['summary'],
                    'strengths': match_result['strengths'],
                    'gaps': match_result['gaps'],
                }
                results.append(db_result)

            except Exception as e:
                print(f"❌ Error matching resume ID {resume.id}: {e}")
                results.append({
                    'resume_id': resume.id,
                    'job_description_id': job.id,
                    'match_score': 0.0,
                    'summary': f"A critical error occurred during matching: {e}",
                    'strengths': [],
                    'gaps': ["Matching process failed for this candidate."],
                })
        
        # Sort results by score, descending
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results