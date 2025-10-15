import pdfplumber
import re
import spacy
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os

class ResumeParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise Exception("Spacy model 'en_core_web_sm' not found. Please run: python -m spacy download en_core_web_sm")

        self.skills_db = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'typescript'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'django', 'flask', 'node.js', 'express', 'spring', 'laravel'],
            'database': ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'sql', 'nosql'],
            'cloud': ['aws', 'azure', 'google cloud', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd'],
            'ml': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'nlp', 'computer vision', 'ai'],
            'tools': ['git', 'jira', 'confluence', 'linux', 'bash', 'powershell', 'vscode', 'eclipse', 'figma'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem solving', 'project management', 'agile']
        }

    def extract_text_from_pdf(self, file_path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text(x_tolerance=1, y_tolerance=1)
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise IOError(f"Error reading PDF file at {file_path}: {e}")
        return text.strip()

    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        email, phone = None, None
        
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            email = email_match.group(0).lower()

        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            phone = phone_match.group(0)

        return {"email": email, "phone": phone}

    def extract_name(self, text: str) -> str:
        doc = self.nlp(text[:500])
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name_parts = ent.text.strip().split()
                if 2 <= len(name_parts) <= 4:
                    return " ".join(part.capitalize() for part in name_parts)
        return "Candidate"

    def extract_skills(self, text: str) -> List[str]:
        found_skills = set()
        text_lower = text.lower()
        
        for category, skills in self.skills_db.items():
            for skill in skills:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.add(skill.strip())
        
        return sorted(list(found_skills))

    def extract_sections(self, text: str) -> Dict[str, str]:
        sections = {}
        section_headers = {
            'experience': r'(?:work\s+)?experience|employment|professional\s+experience',
            'education': r'education|academic|qualifications',
        }
        text_lower = text.lower()
        
        indices = {}
        for name, pattern in section_headers.items():
            match = re.search(pattern, text_lower)
            if match:
                indices[name] = match.start()

        sorted_sections = sorted(indices.items(), key=lambda item: item[1])

        for i, (name, start_index) in enumerate(sorted_sections):
            end_index = sorted_sections[i + 1][1] if i + 1 < len(sorted_sections) else len(text)
            sections[name] = text[start_index:end_index]
        
        return sections

    def extract_experience(self, text: str) -> float:
        evidence = []
        text_lower = text.lower()
        current_year = datetime.now().year

        # --- Evidence 1: Explicit "X years of experience" patterns (High Confidence) ---
        # ⭐ UPDATED: Added more flexible patterns to catch more formats.
        patterns = [
            # Catches "8+ years of professional experience", "5 years experience", "10 years in experience"
            r'(\d+\.?\d*)\+?\s*years?\s*(?:of|in|as)?\s*(?:professional\s*|work\s*|total\s*)?experience',
            # Catches "experience: 8 years", "experience is now 5+ years"
            r'experience\s*(?:is|:)?\s*(?:currently|now|about|over)?\s*(\d+\.?\d*)\+?\s*years?'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for years_str in matches:
                try:
                    if not years_str:
                        continue
                    years = float(years_str)
                    if 0 < years < 40:
                        evidence.append({'value': years, 'confidence': 0.9, 'source': 'regex_direct'})
                except (ValueError, IndexError):
                    continue
    
        # --- Evidence 2: Date Range Calculation (Medium-High Confidence) ---
        work_text = self.extract_sections(text).get('experience', text)
        date_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*(?:19|20)\d{2}\s*-\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*(?:19|20)\d{2}|Present|Current)'
        
        total_months = 0
        date_ranges = re.finditer(date_pattern, work_text, re.IGNORECASE)
        for match in date_ranges:
            try:
                start_str, end_str = match.group(0).split('-')
                start_date = datetime.strptime(start_str.strip(), '%b %Y')
                
                if 'present' in end_str.lower() or 'current' in end_str.lower():
                    end_date = datetime.now()
                else:
                    end_date = datetime.strptime(end_str.strip(), '%b %Y')
                
                duration_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                if duration_months > 0:
                    total_months += duration_months
            except ValueError: continue
        
        if total_months > 0:
            evidence.append({'value': round(total_months / 12.0, 1), 'confidence': 0.75, 'source': 'date_range'})

        # --- Evidence 3: Keyword Analysis (Low Confidence) ---
        if any(k in text_lower for k in ['fresher', 'recent graduate', 'entry-level']):
            evidence.append({'value': 0.0, 'confidence': 0.4, 'source': 'fresher_keyword'})
        if any(k in text_lower for k in ['student', 'undergraduate', 'internship']):
            evidence.append({'value': 0.5, 'confidence': 0.3, 'source': 'student_keyword'})

        if not evidence:
            return 0.0

        evidence.sort(key=lambda x: (x['confidence'], x['value']), reverse=True)
        best_evidence = evidence[0]
        
        print(f"✅ Experience Analysis: Best evidence is {best_evidence['value']:.1f} years (source: {best_evidence['source']})")
        return round(best_evidence['value'], 1)

    def extract_education(self, text: str) -> List[str]:
        education_text = self.extract_sections(text).get('education', text)
        sentences = re.split(r'\.\s+', education_text)
        education_entries = []
        edu_keywords = ['university', 'college', 'institute', 'b.tech', 'm.tech', 'bachelor', 'master', 'ph.d']
        for sentence in sentences:
            if any(key in sentence.lower() for key in edu_keywords) and len(sentence) < 200:
                education_entries.append(sentence.strip())
        return education_entries[:3]

    def parse_resume(self, file_path: str) -> Dict:
        try:
            raw_text = self.extract_text_from_pdf(file_path)
            if not raw_text:
                raise ValueError("PDF text extraction returned empty.")
            
            clean_text = self.clean_text(raw_text)
            contact_info = self.extract_contact_info(raw_text)
            
            result = {
                'name': self.extract_name(raw_text),
                'email': contact_info['email'],
                'phone': contact_info['phone'],
                'skills': self.extract_skills(raw_text),
                'experience': self.extract_experience(raw_text),
                'education': self.extract_education(raw_text),
                'raw_text': raw_text
            }
            print(f"✅ Parsed: {result['name']} | Exp: {result['experience']} yrs | Skills: {len(result['skills'])}")
            return result
        except Exception as e:
            print(f"❌ Critical parsing error for {os.path.basename(file_path)}: {e}")
            return {'name': 'Parsing Failed', 'email': None, 'phone': None, 'skills': [], 'experience': 0.0, 'education': [], 'raw_text': ''}