"""
Simple Bullet Optimizer
AI-powered bullet point improvement using GPT-4.
Standalone, no complex dependencies.
"""
import json
from typing import Optional

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from app.core.config import get_settings


class OptimizationService:
    """
    Simple, focused bullet optimization service.
    Uses GPT-4 for quality rewrites.
    """
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else None
        
        if self.api_key and OPENAI_AVAILABLE:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    async def optimize_bullet(
        self,
        bullet: str,
        job_title: str = "",
        company: str = ""
    ) -> str:
        """
        Optimize a single bullet point.
        
        Args:
            bullet: The original bullet text
            job_title: Context (optional)
            company: Context (optional)
            
        Returns:
            Optimized bullet string
        """
        if not self.client:
            # Fallback: return original
            return bullet
        
        # Build context
        context = []
        if job_title:
            context.append(f"Job Title: {job_title}")
        if company:
            context.append(f"Company: {company}")
        
        context_text = "\n".join(context) if context else "General optimization"
        
        # ROAST Framework Prompt
        system_prompt = """ROLE: You are an expert resume writer and career coach with 15+ years of experience helping professionals land their dream jobs at top tech companies.

OBJECTIVE: Transform a resume bullet point into a highly impactful, ATS-friendly statement that showcases quantifiable achievements and demonstrates clear business value.

AUDIENCE: Your output will be read by:
- Applicant Tracking Systems (ATS) that scan for keywords and metrics
- Recruiters who spend 6-10 seconds per resume
- Hiring managers looking for specific achievements and impact

STYLE:
- Use STAR method (Situation, Task, Action, Result) structure
- Start with strong action verbs (Led, Engineered, Architected, Optimized, etc.)
- Include specific, quantifiable metrics (numbers, percentages, scale)
- CRITICAL: Maintain similar character count to the original (within 10 characters) to preserve resume layout
- If original is ~100 chars, optimized should be ~100 chars (not 150 chars)
- Use industry-standard terminology and keywords
- Format: Single sentence, no bullet character, professional tone
- DO NOT add excessive wordiness that would break single-page layout

TONE: Confident, professional, achievement-focused. Sound like a top performer who delivers measurable results.

LAYOUT CONSTRAINT: The optimized bullet MUST maintain approximately the same length as the original to preserve the one-page resume format. If you make it significantly longer, it will break the layout."""

        target_length = len(bullet)
        min_length = target_length - 10
        max_length = target_length + 10

        user_prompt = f"""CONTEXT:
{context_text}

CURRENT BULLET POINT (Length: {target_length} characters):
{bullet}

TASK: Rewrite this bullet point following the ROAST framework guidelines above. Make it more impactful, specific, and quantifiable while maintaining authenticity.

CRITICAL: Your optimized bullet MUST be between {min_length} and {max_length} characters to preserve the resume's one-page layout.

Return your response as JSON:
{{
  "optimized": "the improved bullet point text here"
}}"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",  # Use GPT-4 for quality
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("optimized", bullet)
            
        except Exception as e:
            print(f"Optimization failed: {e}")
            return bullet

    async def optimize_resume(
        self,
        resume_data: dict,
        job_description: str
    ) -> dict:
        """
        Optimize an entire resume based on a job description.
        Returns a dictionary of {original_bullet: optimized_bullet} mappings.
        """
        if not self.client:
            return {}

        # Extract bullets from resume (experience + projects)
        bullets = []
        for exp in resume_data.get("experience", []):
            bullets.extend(exp.get("bullets", []))
        
        # Also include project bullets
        for proj in resume_data.get("projects", []):
            bullets.extend(proj.get("bullets", []))
        
        if not bullets:
            return {}

        # We'll optimize in batches to save tokens/time
        # For MVP, let's do a smart selection of the top 5 most relevant bullets to optimize
        # or just optimize them all if < 10.
        
        # ROAST Framework Prompt for Full Resume Optimization
        system_prompt = """ROLE: You are a senior resume optimization specialist who helps job seekers tailor their resumes to specific job descriptions, increasing their interview rate by 3-5x.

OBJECTIVE: Analyze the job description and optimize resume bullet points to:
1. Incorporate relevant keywords from the job description
2. Align achievements with the role's requirements
3. Add quantifiable metrics where appropriate
4. Use industry-specific terminology from the JD
5. Only modify bullets that need improvement (don't change perfect ones)

AUDIENCE: Your optimized bullets will be evaluated by:
- ATS systems scanning for JD keywords
- Recruiters matching candidate experience to job requirements
- Hiring managers looking for role-specific achievements

STYLE:
- Maintain the original meaning and authenticity
- Integrate JD keywords naturally (don't force them)
- Add metrics/numbers when contextually appropriate
- Use action verbs that match the job's focus
- Keep each bullet under 150 characters
- Format: Return JSON mapping of original -> optimized bullets

TONE: Professional, confident, achievement-focused. Show how the candidate's experience directly relates to the job requirements."""

        user_prompt = f"""JOB DESCRIPTION:
{job_description[:2000]}

CURRENT RESUME BULLETS:
{json.dumps(bullets[:15], indent=2)}

TASK: Review each bullet point and optimize ONLY the ones that would benefit from:
- Better keyword alignment with the job description
- More specific metrics or quantifiable results
- Stronger action verbs relevant to the role
- Better demonstration of required skills/experience

IMPORTANT: Only return bullets that you've actually improved. If a bullet is already strong and well-aligned, don't include it in the response.

Return JSON mapping of ONLY the changed bullets:
{{
  "original_bullet_text": "optimized_bullet_text",
  ...
}}"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Full optimization failed: {e}")
            return {}
