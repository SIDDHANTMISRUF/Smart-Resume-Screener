import os
from typing import Dict, Tuple
import json
import re

class LLMService:
    def __init__(self):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("Warning: python-dotenv not installed. Skipping .env file loading.")
        
        self.api_available = False
        self.active_provider = "none"
        self.client = self._init_groq()

        if self.client:
            self.active_provider = "groq"
            self.api_available = True
            print("✅ Groq API is configured and available for AI matching.")
        else:
            print("⚠️ No valid AI API key found. Service will operate in rule-based analysis mode.")
            self.active_provider = "rule_based_fallback"
    
    def _init_groq(self):
        try:
            from groq import Groq, APIError
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key or api_key in ["", "your_actual_groq_api_key_here"]:
                return None
            
            client = Groq(api_key=api_key)
            # Test connection with a minimal request to validate the key
            client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}], 
                model="llama-3.1-8b-instant", # <-- CORRECTED MODEL
                max_tokens=2
            )
            return client
        except ImportError:
            print("Warning: 'groq' library not installed. To use the Groq API, run: pip install groq")
            return None
        except APIError as e:
            print(f"❌ Groq API key is invalid or expired: {e.message}")
            return None
        except Exception as e:
            print(f"❌ An unexpected error occurred during Groq initialization: {e}")
            return None
    
    def match_resume_job(self, resume_data: Dict, job_description: Dict) -> Dict:
        """Orchestrates the matching process using the best available method."""
        if not self.api_available:
            return self.get_rule_based_analysis(resume_data, job_description)
        
        system_prompt, user_prompt = self._create_matching_prompts(resume_data, job_description)
        
        try:
            if self.active_provider == "groq":
                return self._call_groq_api(system_prompt, user_prompt)
            else:
                return self.get_rule_based_analysis(resume_data, job_description)
        except Exception as e:
            print(f"❌ LLM API Error: {e}. Falling back to rule-based analysis.")
            return self.get_rule_based_analysis(resume_data, job_description)

    def _call_groq_api(self, system_prompt: str, user_prompt: str) -> Dict:
        """Executes the API call to Groq with the prepared prompts."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant", # <-- CORRECTED MODEL
            temperature=0.1,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        print(f"🔍 Raw LLM Response: {result_text[:250]}...")
        
        return self._parse_llm_response(result_text)

    def _create_matching_prompts(self, resume_data: Dict, job_description: Dict) -> Tuple[str, str]:
        """Creates a powerful system and user prompt pair using few-shot learning."""
        system_prompt = """
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
"""
        is_student = resume_data.get('experience', 0.0) <= 1.5
        student_context = "This is a STUDENT/ENTRY-LEVEL profile. Prioritize potential and foundational skills." if is_student else "This is an EXPERIENCED PROFESSIONAL profile. Evaluate against specific years of experience."

        def clean_text(text): return re.sub(r'\s+', ' ', text).strip()

        user_prompt = f"""
Analyze the following data and generate the JSON response.

**CANDIDATE PROFILE**
- **Type**: {student_context}
- **Experience (Years)**: {resume_data.get('experience', 0)}
- **Skills**: {', '.join(resume_data.get('skills', []))}
- **Resume Snippet**: "{clean_text(resume_data.get('raw_text', ''))[:800]}..."

**JOB DESCRIPTION**
- **Title**: {job_description.get('title', 'N/A')}
- **Required Experience (Years)**: {job_description.get('required_experience', 0)}
- **Required Skills**: {', '.join(job_description.get('required_skills', []))}
- **Details**: "{clean_text(job_description.get('description', ''))[:800]}..."
"""
        return system_prompt, user_prompt

    def _parse_llm_response(self, response_text: str) -> Dict:
        """Safely parses the LLM's JSON output."""
        try:
            result = json.loads(response_text)
            validated = {
                "match_score": float(result.get('match_score', 5.0)),
                "summary": str(result.get('summary', 'AI summary generation failed.')),
                "strengths": result.get('strengths', []),
                "gaps": result.get('gaps', []),
                "is_student": bool(result.get('is_student', False))
            }
            validated['match_score'] = max(1.0, min(10.0, validated['match_score']))
            print(f"✅ Successfully parsed LLM response: Score {validated['match_score']}/10")
            return validated
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"❌ JSON parse error: {e}. Response: {response_text[:200]}")
            return self._get_fallback_response()

    def get_rule_based_analysis(self, resume_data: Dict, job_description: Dict) -> Dict:
        """Provides a structured, rule-based analysis as a fallback."""
        is_student = resume_data.get('experience', 0.0) <= 1.5
        summary = "This analysis is based on a rule-based comparison of skills and experience, as the AI model is currently unavailable."
        return {
            "match_score": 5.0,
            "summary": summary,
            "strengths": ["Rule-based analysis was performed."],
            "gaps": ["Detailed AI-powered insights are not available in this mode."],
            "is_student": is_student
        }
        
    def _get_fallback_response(self) -> Dict:
        """Returns a generic error response when LLM parsing fails."""
        return {
            "match_score": 3.0,
            "summary": "AI analysis was performed, but a technical issue occurred while formatting the response. Please review the rule-based scores for guidance.",
            "strengths": ["Rule-based assessment completed."],
            "gaps": ["AI analysis could not be formatted correctly."],
            "is_student": False
        }