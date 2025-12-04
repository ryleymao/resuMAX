"""
Stage 3: Semantic Cleanup
Fixes broken lines and formatting artifacts WITHOUT changing content.
"""
import re
from typing import List, Dict, Any


class SemanticCleaner:
    """
    Merge broken lines, clean whitespace, normalize formatting
    WITHOUT changing the actual content
    """

    def clean(self, structured_resume: Any) -> Dict[str, Any]:
        """
        Clean up formatting artifacts
        """
        cleaned_sections = []

        # Handle both StructuredResume object and dict
        sections = structured_resume.sections if hasattr(structured_resume, 'sections') else structured_resume.get("sections", [])
        header = structured_resume.header if hasattr(structured_resume, 'header') else structured_resume.get("header", {})

        for section in sections:
            cleaned_entries = []

            # Handle both StructuredSection object and dict
            section_entries = section.entries if hasattr(section, 'entries') else section.get("entries", [])
            section_type = section.section_type if hasattr(section, 'section_type') else section.get("type", "other")
            section_title = section.section_title if hasattr(section, 'section_title') else section.get("title", "")

            for entry in section_entries:
                # Ensure entry is a dict
                if not isinstance(entry, dict):
                    continue

                # Clean bullets: merge broken lines
                if "bullets" in entry and isinstance(entry["bullets"], list):
                    entry["bullets"] = self._merge_broken_bullets(entry["bullets"])

                # Clean main text
                if "main_text" in entry and isinstance(entry["main_text"], list):
                    entry["main_text"] = self._clean_text_list(entry["main_text"])

                cleaned_entries.append(entry)

            cleaned_sections.append({
                "type": section_type,
                "title": section_title,
                "entries": cleaned_entries
            })

        return {
            "header": header,
            "sections": cleaned_sections
        }

    def _merge_broken_bullets(self, bullets: List[str]) -> List[str]:
        """
        Merge bullets that were broken across lines
        Example:
          "Built an AI resume optimizer where users upload resumes, add job"
          "descriptions, and generate tailored resumes."
        Should become:
          "Built an AI resume optimizer where users upload resumes, add job descriptions, and generate tailored resumes."
        """
        if not bullets:
            return []

        merged = []
        current = bullets[0]

        for i in range(1, len(bullets)):
            bullet = bullets[i]

            # Check if this looks like a continuation
            # (doesn't start with bullet char, starts lowercase, previous doesn't end with period)
            is_continuation = (
                not bullet.strip().startswith(("•", "-", "*", "●"))
                and len(bullet) > 0
                and bullet[0].islower()
                and not current.rstrip().endswith((".", "!", "?"))
            )

            if is_continuation:
                # Merge with previous
                current = current.rstrip() + " " + bullet.strip()
            else:
                # Start new bullet
                merged.append(self._clean_bullet(current))
                current = bullet

        merged.append(self._clean_bullet(current))
        return merged

    def _clean_bullet(self, text: str) -> str:
        """
        Clean individual bullet text
        """
        # Remove zero-width characters
        text = re.sub(r'[\u200b-\u200d\ufeff]', '', text)

        # Remove leading bullet characters
        text = re.sub(r'^[•\-\*●]\s*', '', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def _clean_text_list(self, texts: List[str]) -> List[str]:
        """
        Clean list of text lines
        """
        return [self._clean_text(t) for t in texts if t.strip()]

    def _clean_text(self, text: str) -> str:
        """
        Clean single text line
        """
        # Remove zero-width characters
        text = re.sub(r'[\u200b-\u200d\ufeff]', '', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text
