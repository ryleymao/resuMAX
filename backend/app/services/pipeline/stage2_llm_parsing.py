"""
STAGE 2 — STRUCTURAL PARSING (LLM REQUIRED)

Use OpenAI API (GPT-4o-mini or GPT-4o).
This is REQUIRED for accurate parsing.

LLM MUST:
- Identify sections (Experience, Projects, Skills, Education, etc.)
- Recover broken project names
- Recover bullet boundaries
- Infer hierarchy: section → item → bullets
- Identify job titles, companies, dates, locations
- Handle two-column layouts using coordinates

NO rewriting
NO formatting
NO summarizing
NO optimizing

Output: canonical structured JSON exactly matching our schema
If LLM cannot identify a part → mark as "unclassified" (don't drop it)
"""
import json
from typing import List, Dict, Any
from openai import AsyncOpenAI


class LLMStructuralParser:
    """
    Stage 2: Use LLM to identify structure ONLY
    NO rewriting, NO formatting
    """

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def parse_structure(self, raw_text: str, text_spans: List[Any]) -> Dict[str, Any]:
        """
        Use GPT-4o-mini to identify structure from raw text
        Returns canonical JSON matching our Resume schema

        TEMPORARY: Using mock parser for development until OpenAI credits available
        """

        # MOCK MODE - Return hardcoded canonical JSON for development
        # This allows testing Stages 3-7 without API costs
        print("[STAGE 2] 🔧 MOCK MODE: Using hardcoded canonical JSON (swap with GPT-4o later)")
        return self._load_mock_stage2_output()

    async def _real_llm_parse(self, raw_text: str, text_spans: List[Any]) -> Dict[str, Any]:
        """
        REAL LLM PARSING (disabled for now - enable when credits available)
        """
        # Build coordinate hints for two-column detection
        coord_hints = self._build_coordinate_hints(text_spans)

        system_prompt = """You are a resume structure parser. Your ONLY job is to identify the structure of a resume.

CRITICAL RULES:
1. DO NOT rewrite any text
2. DO NOT fix spelling or grammar
3. DO NOT summarize or optimize
4. DO NOT change wording
5. Copy text EXACTLY as provided
6. Your output is purely structural metadata

YOUR TASKS:
- Identify sections: Experience, Projects, Skills, Education, Certifications, Awards, etc.
- For each section, identify individual entries
- For each entry, extract:
  * Company/Institution/Project name
  * Title/Role/Degree
  * Dates (start_date, end_date, current flag)
  * Location
  * Bullet points (copy EXACTLY)
  * Technologies/skills mentioned
- Recover broken project names (e.g., "resu" on one line, "MAX" on next → "resuMAX")
- Identify bullet boundaries even if bullets span multiple lines
- Handle two-column layouts using coordinate hints
- If you cannot identify something, mark it as "unclassified" - DO NOT drop content

OUTPUT FORMAT (strict JSON):
{
  "header": {
    "name": "Exact Name",
    "email": "email@example.com",
    "phone": "555-1234",
    "location": "City, State",
    "linkedin": "linkedin.com/in/username",
    "github": "github.com/username",
    "website": "example.com"
  },
  "summary": "If present, copy exactly",
  "experience": [
    {
      "company": "Company Name",
      "title": "Job Title",
      "location": "City, State",
      "start_date": "Jan 2020",
      "end_date": "Present",
      "current": true,
      "bullets": ["Exact bullet 1", "Exact bullet 2"],
      "technologies": ["Python", "React"]
    }
  ],
  "projects": [
    {
      "name": "Project Name",
      "description": "One-line description if available",
      "url": "github.com/user/project",
      "start_date": "Jan 2020",
      "end_date": "Dec 2020",
      "bullets": ["Exact bullet 1"],
      "technologies": ["Python", "Docker"]
    }
  ],
  "education": [
    {
      "institution": "School Name",
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "location": "City, State",
      "start_date": "Sep 2016",
      "end_date": "May 2020",
      "gpa": "3.8",
      "honors": ["Dean's List"],
      "coursework": ["Data Structures", "Algorithms"]
    }
  ],
  "skills": {
    "Languages": ["Python", "JavaScript"],
    "Frameworks": ["React", "Django"],
    "Tools": ["Git", "Docker"]
  },
  "certifications": [
    {
      "name": "AWS Certified Developer",
      "issuer": "Amazon",
      "date": "Jan 2020",
      "credential_id": "ABC123"
    }
  ],
  "awards": [
    {
      "name": "Best Hackathon Project",
      "issuer": "HackMIT",
      "date": "Sep 2019",
      "description": "Won 1st place"
    }
  ],
  "unclassified": [
    {
      "title": "Section Title",
      "content": "Any content that doesn't fit above categories"
    }
  ]
}
"""

        user_prompt = f"""Parse the structure of this resume. Copy ALL text EXACTLY.

{coord_hints}

Resume text:
{raw_text}

Return pure structural JSON with exact text copied. Use the exact format specified in the system prompt."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Use GPT-4o-mini as specified
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,  # Deterministic
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            # If LLM fails, we CANNOT continue with fallback
            # Structured parsing is REQUIRED
            raise RuntimeError(f"LLM structural parsing REQUIRED but failed: {str(e)}")

    def _build_coordinate_hints(self, text_spans: List[Any]) -> str:
        """
        Build hints about text positions for two-column detection
        """
        if not text_spans or len(text_spans) < 10:
            return ""

        # Calculate average x-position
        x_positions = [span.x0 for span in text_spans[:20]]
        avg_x = sum(x_positions) / len(x_positions)

        # Detect if there are two distinct columns
        left_col = [x for x in x_positions if x < avg_x - 50]
        right_col = [x for x in x_positions if x > avg_x + 50]

        if len(left_col) > 3 and len(right_col) > 3:
            return "\n[COORDINATE HINT: This resume appears to have a two-column layout. Text on the left and right should be merged appropriately (e.g., company on left, location on right).]"

        return ""

    def _mock_parse_structure(self, raw_text: str, text_spans: List[Any]) -> Dict[str, Any]:
        """
        MOCK PARSER for development without API costs
        Uses rule-based extraction to produce valid canonical JSON

        SWAP THIS WITH _real_llm_parse() when credits available
        """
        import re

        lines = raw_text.split("\n")

        # Initialize output
        result = {
            "header": {
                "name": "",
                "email": "",
                "phone": "",
                "location": "",
                "linkedin": "",
                "github": "",
                "website": ""
            },
            "summary": "",
            "experience": [],
            "projects": [],
            "education": [],
            "skills": {},
            "certifications": [],
            "awards": [],
            "unclassified": []
        }

        # Extract header from first few lines
        if lines:
            result["header"]["name"] = lines[0].strip()

        # Find email, phone, linkedin, github
        for line in lines[:10]:
            if "@" in line and not result["header"]["email"]:
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line)
                if email_match:
                    result["header"]["email"] = email_match.group(0)

            if re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', line) and not result["header"]["phone"]:
                phone_match = re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', line)
                if phone_match:
                    result["header"]["phone"] = phone_match.group(0)

            if "linkedin.com" in line.lower():
                result["header"]["linkedin"] = line.strip()

            if "github.com" in line.lower():
                result["header"]["github"] = line.strip()

        # Section detection
        section_keywords = {
            "experience": ["experience", "work history", "employment"],
            "projects": ["projects", "portfolio"],
            "education": ["education", "academic"],
            "skills": ["skills", "technologies", "technical skills"],
            "certifications": ["certifications", "certificates", "licenses"],
            "awards": ["awards", "honors", "achievements"]
        }

        current_section = None
        current_entry = None

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Skip empty lines
            if not line_lower:
                continue

            # Check if this is a section header
            for section_name, keywords in section_keywords.items():
                if any(keyword in line_lower for keyword in keywords):
                    current_section = section_name
                    current_entry = None
                    break

            # Parse section content
            if current_section == "experience":
                # Detect job entry (usually has dates or company name)
                if re.search(r'\d{4}|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', line_lower):
                    # Save previous entry
                    if current_entry:
                        result["experience"].append(current_entry)

                    # Start new entry
                    current_entry = {
                        "company": "",
                        "title": "",
                        "location": "",
                        "start_date": "",
                        "end_date": "",
                        "current": "present" in line_lower,
                        "bullets": [],
                        "technologies": []
                    }

                    # Try to extract dates
                    date_match = re.findall(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)[\s,]*\d{4}|\d{4}', line_lower)
                    if date_match:
                        if len(date_match) >= 2:
                            current_entry["start_date"] = date_match[0]
                            current_entry["end_date"] = date_match[1] if not current_entry["current"] else "Present"
                        elif len(date_match) == 1:
                            current_entry["start_date"] = date_match[0]

                    # Extract company/title (simple heuristic)
                    clean_line = re.sub(r'\d{4}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|present', '', line_lower).strip()
                    if "|" in clean_line:
                        parts = clean_line.split("|")
                        current_entry["company"] = parts[0].strip()
                        current_entry["title"] = parts[1].strip() if len(parts) > 1 else ""
                    else:
                        current_entry["company"] = clean_line

                # Detect bullet points
                elif current_entry and (line.strip().startswith("•") or line.strip().startswith("-") or line.strip().startswith("*")):
                    bullet = line.strip().lstrip("•-*").strip()
                    current_entry["bullets"].append(bullet)

            elif current_section == "projects":
                # Similar logic for projects
                if re.search(r'\d{4}|github|gitlab|project', line_lower):
                    if current_entry:
                        result["projects"].append(current_entry)

                    current_entry = {
                        "name": "",
                        "description": "",
                        "url": "",
                        "start_date": "",
                        "end_date": "",
                        "bullets": [],
                        "technologies": []
                    }

                    # Extract project name
                    current_entry["name"] = line.strip()

                elif current_entry and (line.strip().startswith("•") or line.strip().startswith("-")):
                    bullet = line.strip().lstrip("•-*").strip()
                    current_entry["bullets"].append(bullet)

            elif current_section == "education":
                if re.search(r'university|college|bachelor|master|phd|b\.s\.|m\.s\.|degree', line_lower):
                    if current_entry:
                        result["education"].append(current_entry)

                    current_entry = {
                        "institution": "",
                        "degree": "",
                        "field": "",
                        "location": "",
                        "start_date": "",
                        "end_date": "",
                        "gpa": "",
                        "honors": [],
                        "coursework": []
                    }

                    current_entry["institution"] = line.strip()

            elif current_section == "skills":
                # Extract skills (comma-separated or bullet points)
                if ":" in line:
                    parts = line.split(":", 1)
                    category = parts[0].strip()
                    skills = [s.strip() for s in parts[1].split(",")]
                    result["skills"][category] = skills
                elif line.strip().startswith("•") or line.strip().startswith("-"):
                    skills = [s.strip() for s in line.strip().lstrip("•-*").split(",")]
                    result["skills"]["General"] = result["skills"].get("General", []) + skills

        # Add last entry
        if current_entry:
            if current_section == "experience":
                result["experience"].append(current_entry)
            elif current_section == "projects":
                result["projects"].append(current_entry)
            elif current_section == "education":
                result["education"].append(current_entry)

        print(f"[MOCK PARSER] Extracted: {len(result['experience'])} experience, {len(result['projects'])} projects, {len(result['education'])} education")

        return result

    def _load_mock_stage2_output(self) -> Dict[str, Any]:
        """
        HARDCODED CANONICAL JSON for development/testing
        This is Ryley's actual resume in perfect canonical format

        SWAP THIS with _real_llm_parse() when GPT-4o credits available
        """
        return {
            "header": {
                "name": "Ryley Mao",
                "email": "rymao_@outlook.com",
                "phone": "(607)232-8826",
                "location": "",
                "linkedin": "linkedin.com/in/ryley-mao",
                "github": "github.com/rylemao",
                "website": "rymao.info"
            },
            "summary": "",
            "experience": [
                {
                    "company": "OPEN SOURCE",
                    "title": "Software Engineer",
                    "location": "Remote",
                    "start_date": "Sep 2025",
                    "end_date": "Nov 2025",
                    "current": False,
                    "bullets": [
                        "Built scalable backend APIs and authentication systems using Python + FastAPI, improving performance for 1k+ users",
                        "Developed and optimized automated test suites and CI/CD workflows, reducing pipeline runtime by 35%",
                        "Refactored and maintained large codebases, improving stability, maintainability, and performance optimization",
                        "Contributed modular, reusable code and technical documentation, accelerating onboarding for new contributors"
                    ],
                    "technologies": ["Python", "FastAPI"]
                },
                {
                    "company": "JPMorgan Chase",
                    "title": "Software Engineer Intern",
                    "location": "New York, NY",
                    "start_date": "Jun 2025",
                    "end_date": "Aug 2025",
                    "current": False,
                    "bullets": [
                        "Integrated Kafka message queues into Spring Boot microservices, processing 1,000+ financial transactions asynchronously",
                        "Implemented data validation and persistence using H2 SQL and Spring Data JPA, ensuring reliable transaction handling",
                        "Developed RESTful API integration for rewards service, exposing /balance endpoint handling 500+ requests/sec",
                        "Engineered backend services with robust error handling and transaction logging, ensuring system reliability and auditability"
                    ],
                    "technologies": ["Kafka", "Spring Boot", "SQL", "JPA"]
                },
                {
                    "company": "Tesla",
                    "title": "Infotainment Technician",
                    "location": "Fremont, CA",
                    "start_date": "Apr 2021",
                    "end_date": "Aug 2023",
                    "current": False,
                    "bullets": [
                        "Developed Python automation scripts for diagnostics, saving ~20 technician hours per month across 50+ daily repairs",
                        "Diagnosed, debugged, and optimized firmware/software on 1,000+ vehicles, improving diagnostic accuracy by 15%",
                        "Engineered Python scripts to automate data driven workflows, improving efficiency and reducing manual errors"
                    ],
                    "technologies": ["Python"]
                }
            ],
            "projects": [
                {
                    "name": "ResuMAX",
                    "description": "AI resume optimizer with job matching",
                    "url": "",
                    "start_date": "",
                    "end_date": "",
                    "bullets": [
                        "Built an AI resume optimizer where users upload resumes, add job descriptions, and generate tailored outputs end to end",
                        "Implemented backend APIs for resumes, job descriptions, and optimization sessions with secure Firebase authentication",
                        "Added semantic search and embedding based scoring to match resume content to job requirements more accurately",
                        "Developed services for text parsing, LLM rewriting, and generating downloadable docx/pdf files backed by cloud storage"
                    ],
                    "technologies": ["FastAPI", "PostgreSQL", "Firebase Auth", "AWS", "OpenAI API"]
                },
                {
                    "name": "Web Agent",
                    "description": "AI web agent for autonomous task completion",
                    "url": "",
                    "start_date": "",
                    "end_date": "",
                    "bullets": [
                        "Built an AI web agent that receives natural language tasks and autonomously navigates websites to complete them",
                        "Implemented DOM based navigation with LLM reasoning and perceptual hashing for UI tracking, reducing costs 90%",
                        "Integrated multi LLM support with adjustable temperature and token limits for deterministic or exploratory behavior",
                        "Developed multi agent architecture with persistent browser sessions, enabling continuous multi-task workflows"
                    ],
                    "technologies": ["Python", "Playwright", "OpenAI API"]
                },
                {
                    "name": "HintAI",
                    "description": "Realtime coding assistant with semantic search",
                    "url": "",
                    "start_date": "",
                    "end_date": "",
                    "bullets": [
                        "Built a realtime coding assistant with <50ms semantic search over 1,000+ embeddings using pgvector HNSW indexing",
                        "Chrome extension streams code via WebSocket; parses structure to detect patterns (two-pointer, DP), generates hints",
                        "Implemented RAG retrieval with vector + metadata search; Redis caching and prompt optimization cut API costs 65%",
                        "Shipped Dockerized FastAPI with async endpoints, 87% test coverage; open sourced with Two Sum/3Sum demo"
                    ],
                    "technologies": ["Python", "WebSocket", "PostgreSQL", "Redis", "Docker"]
                }
            ],
            "education": [
                {
                    "institution": "University of California, San Diego",
                    "degree": "B.S. in Mathematics-Computer Science",
                    "field": "Mathematics-Computer Science",
                    "location": "La Jolla, CA",
                    "start_date": "",
                    "end_date": "Graduated",
                    "gpa": "",
                    "honors": [],
                    "coursework": []
                }
            ],
            "skills": {
                "Languages & Frameworks": ["Python", "Java", "JavaScript", "FastAPI", "Node.js", "Express.js", "Next.js", "React"],
                "Backend & Databases": ["REST APIs", "Async Services", "Microservices", "SQL (PostgreSQL)", "NoSQL (MongoDB, Redis)", "Kafka"],
                "Cloud & DevOps": ["Docker", "Git", "CI/CD", "AWS (EC2, S3, Lambda)", "GCP (Cloud Run, Pub/Sub)", "Firebase (Auth/Functions)"]
            },
            "certifications": [],
            "awards": [],
            "unclassified": []
        }
