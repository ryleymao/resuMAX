"""
Diff Engine - Compares text and highlights changes
Used for showing users what the LLM changed in their resume bullets.

This module is deterministic (no LLM) - pure text comparison.
"""
from typing import List, Dict, Any
from difflib import SequenceMatcher
from pydantic import BaseModel


class TextChange(BaseModel):
    """Represents a single change in text"""
    type: str  # "added", "removed", "unchanged"
    text: str
    start_index: int
    end_index: int


class DiffResult(BaseModel):
    """Result of comparing two texts"""
    original: str
    modified: str
    changes: List[TextChange]
    similarity_score: float  # 0-1


class DiffEngine:
    """
    Compares two versions of text and produces granular change tracking.
    
    Use Cases:
    - Show user what LLM changed in their bullet
    - Highlight added keywords
    - Track formatting changes
    
    Example:
        engine = DiffEngine()
        result = engine.compare(
            "Managed team projects",
            "Led cross-functional team of 5 engineers on 3 projects"
        )
        # result.changes shows word-level differences
    """
    
    @staticmethod
    def compare(original: str, modified: str) -> DiffResult:
        """
        Compare two strings and return detailed diff.
        
        Args:
            original: The original text (before LLM)
            modified: The modified text (after LLM)
            
        Returns:
            DiffResult with word-level changes
        """
        # Calculate similarity score
        similarity = SequenceMatcher(None, original, modified).ratio()
        
        # Get word-level changes
        changes = DiffEngine._get_word_changes(original, modified)
        
        return DiffResult(
            original=original,
            modified=modified,
            changes=changes,
            similarity_score=similarity
        )
    
    @staticmethod
    def _get_word_changes(original: str, modified: str) -> List[TextChange]:
        """
        Get word-level changes between two strings.
        
        Returns a list of TextChange objects that can be used to:
        - Highlight in yellow (changed)
        - Highlight in green (added)
        - Highlight in red (removed)
        """
        # Split into words while preserving positions
        original_words = original.split()
        modified_words = modified.split()
        
        # Use SequenceMatcher for intelligent diffing
        matcher = SequenceMatcher(None, original_words, modified_words)
        
        changes = []
        current_pos = 0
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Unchanged text
                text = ' '.join(original_words[i1:i2])
                changes.append(TextChange(
                    type="unchanged",
                    text=text,
                    start_index=current_pos,
                    end_index=current_pos + len(text)
                ))
                current_pos += len(text) + 1  # +1 for space
                
            elif tag == 'replace':
                # Changed text
                old_text = ' '.join(original_words[i1:i2])
                new_text = ' '.join(modified_words[j1:j2])
                
                # Mark as removed (from original perspective)
                changes.append(TextChange(
                    type="removed",
                    text=old_text,
                    start_index=current_pos,
                    end_index=current_pos + len(old_text)
                ))
                
                # Mark as added (from modified perspective)
                changes.append(TextChange(
                    type="added",
                    text=new_text,
                    start_index=current_pos,
                    end_index=current_pos + len(new_text)
                ))
                
                current_pos += len(new_text) + 1
                
            elif tag == 'delete':
                # Removed from original
                text = ' '.join(original_words[i1:i2])
                changes.append(TextChange(
                    type="removed",
                    text=text,
                    start_index=current_pos,
                    end_index=current_pos + len(text)
                ))
                current_pos += 1
                
            elif tag == 'insert':
                # Added in modified
                text = ' '.join(modified_words[j1:j2])
                changes.append(TextChange(
                    type="added",
                    text=text,
                    start_index=current_pos,
                    end_index=current_pos + len(text)
                ))
                current_pos += len(text) + 1
        
        return changes
    
    @staticmethod
    def highlight_keywords(
        text: str,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Identify keyword positions in text for highlighting.
        
        Used to show user which keywords from the job description
        are present in their resume.
        
        Args:
            text: The text to search
            keywords: List of keywords to find
            
        Returns:
            List of {keyword, start, end} dicts
        """
        highlights = []
        text_lower = text.lower()
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            start = 0
            
            while True:
                pos = text_lower.find(keyword_lower, start)
                if pos == -1:
                    break
                    
                highlights.append({
                    "keyword": keyword,
                    "start": pos,
                    "end": pos + len(keyword),
                    "matched_text": text[pos:pos + len(keyword)]
                })
                
                start = pos + 1
        
        # Sort by position
        highlights.sort(key=lambda x: x["start"])
        return highlights


# Example usage and testing
if __name__ == "__main__":
    # Example 1: Simple change
    engine = DiffEngine()
    result = engine.compare(
        "Managed team projects",
        "Led cross-functional team of 5 engineers on 3 projects"
    )
    print("Similarity:", result.similarity_score)
    print("Changes:", len(result.changes))
    
    # Example 2: Keyword highlighting
    text = "Built Python application using FastAPI and PostgreSQL"
    keywords = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    highlights = engine.highlight_keywords(text, keywords)
    print("Found keywords:", [h["keyword"] for h in highlights])
