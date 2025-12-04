"""
Job Description Analysis Service
Extracts keywords, identifies gaps, and analyzes alignment with resume.
Uses GPT-4o-mini for cost optimization.
"""
import re
from typing import List, Dict, Any
from pydantic import BaseModel

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    openai = None
    OPENAI_AVAILABLE = False

from app.core.config import get_settings


class JobAnalysisResult(BaseModel):
    """Result of job description analysis"""
    required_keywords: List[str]
    preferred_keywords: List[str]
    missing_skills: List[str]
    role_level: str  # "Entry", "Mid", "Senior", "Staff"
    industry: str
    key_responsibilities: List[str]
    

class ResumeGapAnalysis(BaseModel):
    """Gap analysis between resume and job"""
    missing_keywords: List[str]
    weak_bullets: List[Dict[str, Any]]  # {bullet_text, reason, suggestion}
    alignment_score: float  # 0-100
    recommendations: List[str]


class JobAnalyzer:
    """
    Analyzes job descriptions to extract requirements and compare with resumes.
    Uses GPT-4o-mini for cost-effective analysis.
    """
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else None
        
        if self.api_key and OPENAI_AVAILABLE:
            openai.api_key = self.api_key
    
    async def analyze_job_description(self, job_description: str) -> JobAnalysisResult:
        """
        Extract key information from job description.
        Uses GPT-4o-mini for cost optimization.
        """
        if not OPENAI_AVAILABLE or not self.api_key:
            # Fallback: basic keyword extraction
            return self._extract_keywords_basic(job_description)
        
        # ROAST Framework Prompt
        system_prompt = """ROLE: You are a technical recruiter and job market analyst with expertise in parsing job descriptions to extract critical hiring signals.

OBJECTIVE: Analyze a job description and extract structured, actionable intelligence including:
- Required vs preferred skills/technologies
- Role seniority level
- Industry classification
- Core responsibilities
- Missing skills that candidates should highlight

AUDIENCE: Your analysis will be used by:
- Job seekers optimizing their resumes for this specific role
- Resume optimization algorithms matching candidates to requirements
- Career coaches providing targeted advice

STYLE:
- Extract keywords that appear in "Required", "Must Have", "Required Qualifications" sections as required_keywords
- Extract keywords from "Preferred", "Nice to Have", "Bonus" sections as preferred_keywords
- Identify role level from titles and responsibilities (Entry/Mid/Senior/Staff)
- List 3-7 key responsibilities that define the role
- Return ONLY valid JSON matching the exact schema

TONE: Analytical, precise, and actionable. Focus on what recruiters and ATS systems actually look for."""

        schema_instruction = """
Return ONLY valid JSON matching this exact schema:
{
  "required_keywords": ["keyword1", "keyword2", ...],
  "preferred_keywords": ["keyword1", "keyword2", ...],
  "missing_skills": [],
  "role_level": "Entry|Mid|Senior|Staff",
  "industry": "string",
  "key_responsibilities": ["resp1", "resp2", ...]
}"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # Cost-optimized model
                messages=[
                    {"role": "system", "content": system_prompt + schema_instruction},
                    {"role": "user", "content": f"Analyze this job description:\n\n{job_description}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return JobAnalysisResult(**result)
            
        except Exception as e:
            print(f"LLM analysis failed: {e}, falling back to basic extraction")
            return self._extract_keywords_basic(job_description)
    
    async def analyze_resume_gaps(
        self,
        resume_text: str,
        job_analysis: JobAnalysisResult
    ) -> ResumeGapAnalysis:
        """
        Compare resume against job requirements.
        Identify missing keywords and weak bullets.
        """
        if not OPENAI_AVAILABLE or not self.api_key:
            return self._analyze_gaps_basic(resume_text, job_analysis)
        
        # ROAST Framework Prompt
        system_prompt = """ROLE: You are a senior career coach and resume strategist who helps candidates identify gaps between their resume and job requirements, providing actionable improvement recommendations.

OBJECTIVE: Perform a comprehensive gap analysis comparing the candidate's resume against the job requirements to:
1. Identify missing critical keywords from the job description
2. Find weak bullet points that lack impact, metrics, or relevance
3. Calculate an alignment score (0-100) based on keyword match and content quality
4. Provide specific, actionable recommendations for improvement

AUDIENCE: Your analysis will be used by:
- Job seekers who need to understand how their resume compares to job requirements
- Resume optimization tools that need to highlight improvement areas
- Career coaches providing targeted feedback

STYLE:
- Be specific and actionable (not vague)
- Focus on keywords that actually appear in the job description
- Identify bullets that are vague, lack metrics, or don't demonstrate impact
- Provide concrete suggestions (not just "improve this")
- Return ONLY valid JSON matching the exact schema

TONE: Constructive, supportive, and direct. Help the candidate understand exactly what to improve and why."""

        schema_instruction = """
Return ONLY valid JSON matching this exact schema:
{
  "missing_keywords": ["keyword1", ...],
  "weak_bullets": [
    {"bullet_text": "string", "reason": "string", "suggestion": "string"}
  ],
  "alignment_score": 0-100,
  "recommendations": ["rec1", "rec2", ...]
}"""

        context = f"""Job Requirements:
{job_analysis.model_dump_json(indent=2)}

Resume:
{resume_text}"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt + schema_instruction},
                    {"role": "user", "content": context}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return ResumeGapAnalysis(**result)
            
        except Exception as e:
            print(f"Gap analysis failed: {e}")
            return self._analyze_gaps_basic(resume_text, job_analysis)
    
    def _extract_keywords_basic(self, text: str) -> JobAnalysisResult:
        """Fallback: basic keyword extraction using regex and heuristics"""
        lines = text.split('\n')
        
        # Common tech keywords
        tech_patterns = [
            r'\b(Python|Java|JavaScript|TypeScript|React|Angular|Vue|Node\.js|Django|FastAPI|Flask)\b',
            r'\b(AWS|Azure|GCP|Docker|Kubernetes|CI/CD|Git|Jenkins)\b',
            r'\b(SQL|PostgreSQL|MongoDB|Redis|MySQL)\b',
            r'\b(Machine Learning|AI|NLP|Deep Learning|TensorFlow|PyTorch)\b',
        ]
        
        keywords = set()
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.update(matches)
        
        return JobAnalysisResult(
            required_keywords=list(keywords)[:10],
            preferred_keywords=[],
            missing_skills=[],
            role_level="Mid",
            industry="Technology",
            key_responsibilities=[]
        )
    
    def _analyze_gaps_basic(
        self,
        resume_text: str,
        job_analysis: JobAnalysisResult
    ) -> ResumeGapAnalysis:
        """Fallback: basic gap analysis"""
        resume_lower = resume_text.lower()
        
        missing = [
            keyword for keyword in job_analysis.required_keywords
            if keyword.lower() not in resume_lower
        ]
        
        return ResumeGapAnalysis(
            missing_keywords=missing,
            weak_bullets=[],
            alignment_score=max(0, 100 - len(missing) * 5),
            recommendations=[f"Add '{kw}' to your resume" for kw in missing[:3]]
        )
