"""
Stage 2: Structural Segmentation
Uses LLM (Claude Haiku) to identify structure ONLY.
NO rewriting, NO cleaning - pure structural identification.
"""
import json
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class StructuredSection:
    """A section with its entries"""
    section_type: str  # "experience", "education", "projects", "skills", etc.
    section_title: str
    entries: List[Dict[str, Any]]
    start_line: int
    end_line: int


@dataclass
class StructuredResume:
    """Resume with identified structure"""
    header: Dict[str, Any]
    sections: List[StructuredSection]
    raw_lines: List[str]


class StructuralSegmenter:
    """
    Stage 2: Identify structure using LLM

    This stage ONLY identifies:
    - Section boundaries
    - Entry boundaries
    - Bullet points
    - Headers vs content

    It does NOT:
    - Rewrite text
    - Fix spelling
    - Merge broken lines
    - Clean formatting
    """

    def __init__(self, llm_client=None):
        """
        llm_client: AsyncOpenAI or AsyncAnthropic client
        """
        self.llm_client = llm_client

    async def segment(self, raw_text: str, blocks: List[Any]) -> StructuredResume:
        """
        Identify structure from raw text
        """
        if not self.llm_client:
            # Fallback: basic rule-based segmentation
            return self._fallback_segment(raw_text)

        # LLM prompt for structural identification ONLY
        system_prompt = """You are a resume structure identifier.

Your ONLY task is to identify the STRUCTURE of a resume:
1. Identify section boundaries (Experience, Education, Skills, Projects, etc.)
2. Identify individual entries within each section
3. Identify bullet points vs non-bullet text
4. Identify header information (name, contact)

CRITICAL RULES:
- DO NOT rewrite any text
- DO NOT fix spelling or grammar
- DO NOT merge lines
- DO NOT clean formatting
- Copy text EXACTLY as provided
- Your output is purely structural metadata

Output JSON format:
{
  "header": {
    "name": "exact name from resume",
    "contact": ["exact contact lines"]
  },
  "sections": [
    {
      "type": "experience|education|projects|skills|other",
      "title": "exact section title",
      "entries": [
        {
          "type": "job|project|school|skill_category",
          "main_text": ["exact lines for company/title/dates"],
          "bullets": ["exact bullet text", "..."],
          "metadata": {"any structural notes"}
        }
      ]
    }
  ]
}"""

        user_prompt = f"""Identify the structure of this resume text. Copy ALL text EXACTLY.

Resume text:
{raw_text}

Return pure structural JSON with exact text copied."""

        try:
            # Use GPT-3.5-turbo for cost-effective structural analysis
            response = await self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,  # Deterministic
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return self._parse_llm_structure(result, raw_text)

        except Exception as e:
            print(f"LLM segmentation failed: {e}")
            return self._fallback_segment(raw_text)

    def _fallback_segment(self, raw_text: str) -> StructuredResume:
        """
        Rule-based fallback when LLM unavailable
        """
        lines = raw_text.split("\n")
        sections = []
        header = {"name": lines[0] if lines else "", "contact": []}

        # Simple heuristic section detection
        section_keywords = ["experience", "education", "skills", "projects"]
        current_section = None
        current_entries = []

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Check if this is a section header
            is_section = any(keyword in line_lower for keyword in section_keywords)

            if is_section:
                # Save previous section
                if current_section:
                    sections.append(StructuredSection(
                        section_type=current_section["type"],
                        section_title=current_section["title"],
                        entries=current_entries,
                        start_line=current_section["start"],
                        end_line=i - 1
                    ))

                # Start new section
                current_section = {
                    "type": next((k for k in section_keywords if k in line_lower), "other"),
                    "title": line.strip(),
                    "start": i
                }
                current_entries = []

        # Add last section
        if current_section:
            sections.append(StructuredSection(
                section_type=current_section["type"],
                section_title=current_section["title"],
                entries=current_entries,
                start_line=current_section["start"],
                end_line=len(lines) - 1
            ))

        return StructuredResume(
            header=header,
            sections=sections,
            raw_lines=lines
        )

    def _parse_llm_structure(self, llm_output: Dict, raw_text: str) -> StructuredResume:
        """
        Convert LLM JSON output to StructuredResume
        """
        sections = []
        for sec_data in llm_output.get("sections", []):
            section = StructuredSection(
                section_type=sec_data.get("type", "other"),
                section_title=sec_data.get("title", ""),
                entries=sec_data.get("entries", []),
                start_line=0,  # Could calculate from text matching
                end_line=0
            )
            sections.append(section)

        return StructuredResume(
            header=llm_output.get("header", {}),
            sections=sections,
            raw_lines=raw_text.split("\n")
        )
