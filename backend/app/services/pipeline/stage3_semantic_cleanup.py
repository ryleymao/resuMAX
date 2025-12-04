"""
STAGE 3 — SEMANTIC CLEANUP (CODE ONLY)

Pure deterministic cleanup:
- merge broken lines
- fix hyphenated line breaks
- remove duplicate words from PDF extraction
- normalize whitespace
- preserve meaning and original wording

The LLM is NOT allowed to rewrite content here.
"""
import re
from typing import List, Dict, Any


class SemanticCleaner:
    """
    Stage 3: Deterministic text cleanup
    NO rewriting, NO interpretation
    """

    def clean(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up text artifacts while preserving meaning
        """
        cleaned = structured_data.copy()

        # Clean header
        if "header" in cleaned:
            for key in cleaned["header"]:
                if isinstance(cleaned["header"][key], str):
                    cleaned["header"][key] = self._clean_text(cleaned["header"][key])

        # Clean summary
        if "summary" in cleaned and cleaned["summary"]:
            cleaned["summary"] = self._clean_text(cleaned["summary"])

        # Clean experience
        if "experience" in cleaned:
            cleaned["experience"] = [self._clean_entry(e) for e in cleaned["experience"]]

        # Clean projects
        if "projects" in cleaned:
            cleaned["projects"] = [self._clean_entry(e) for e in cleaned["projects"]]

        # Clean education
        if "education" in cleaned:
            cleaned["education"] = [self._clean_entry(e) for e in cleaned["education"]]

        # Clean certifications
        if "certifications" in cleaned:
            cleaned["certifications"] = [self._clean_entry(e) for e in cleaned["certifications"]]

        # Clean awards
        if "awards" in cleaned:
            cleaned["awards"] = [self._clean_entry(e) for e in cleaned["awards"]]

        # Clean skills
        if "skills" in cleaned:
            for category in cleaned["skills"]:
                if isinstance(cleaned["skills"][category], list):
                    cleaned["skills"][category] = [
                        self._clean_text(s) for s in cleaned["skills"][category]
                    ]

        return cleaned

    def _clean_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Clean all text fields in an entry"""
        cleaned = {}
        for key, value in entry.items():
            if isinstance(value, str):
                cleaned[key] = self._clean_text(value)
            elif isinstance(value, list):
                if all(isinstance(item, str) for item in value):
                    # List of strings (bullets, technologies, etc.)
                    cleaned[key] = [self._clean_text(item) for item in value]
                else:
                    cleaned[key] = value
            else:
                cleaned[key] = value
        return cleaned

    def _clean_text(self, text: str) -> str:
        """
        Clean individual text string
        - Remove zero-width characters
        - Fix hyphenated line breaks
        - Remove duplicate words
        - Normalize whitespace
        """
        if not text:
            return text

        # Remove zero-width characters
        text = re.sub(r'[\u200b-\u200d\ufeff]', '', text)

        # Fix hyphenated line breaks (e.g., "optimiza-\ntion" → "optimization")
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)

        # Remove duplicate words that occur at line breaks
        # (e.g., "word word" → "word")
        text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text)

        # Normalize whitespace (multiple spaces → single space)
        text = re.sub(r'\s+', ' ', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text
