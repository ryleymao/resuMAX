"""
Font Metrics Calculator
Measures exact character widths for precise layout calculations.
"""
from typing import Dict, Tuple
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch


class FontMetrics:
    """
    Calculates exact character widths for layout
    """

    # Standard font widths (approximate) for common fonts
    # These are in points per character for size 1
    ARIAL_WIDTHS = {
        'default': 0.5,  # Average character width ratio
        ' ': 0.278,
        'i': 0.278,
        'l': 0.278,
        'm': 0.833,
        'w': 0.722,
        'W': 0.944,
        'M': 0.833,
    }

    def __init__(self, font_name: str = "Helvetica", font_size: float = 10):
        self.font_name = font_name
        self.font_size = font_size

    def measure_text_width(self, text: str) -> float:
        """
        Calculate exact width of text in points
        """
        try:
            # Try to get actual font metrics from reportlab
            font = pdfmetrics.getFont(self.font_name)
            width = font.stringWidth(text, self.font_size)
            return width / 72.0  # Convert to inches
        except:
            # Fallback: use approximation
            char_width_ratio = sum(
                self.ARIAL_WIDTHS.get(char, 0.5) for char in text
            ) / len(text) if text else 0
            return (len(text) * char_width_ratio * self.font_size) / 72.0

    def measure_line_width(self, text: str) -> float:
        """
        Measure width of a single line in inches
        """
        return self.measure_text_width(text)

    def calculate_line_breaks(self, text: str, max_width_inches: float) -> list[str]:
        """
        Calculate where to break text into lines given max width
        Returns list of lines
        """
        words = text.split()
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            word_width = self.measure_text_width(word + " ")

            if current_width + word_width <= max_width_inches:
                current_line.append(word)
                current_width += word_width
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def hyphenate_word(self, word: str, max_width_inches: float) -> Tuple[str, str]:
        """
        Hyphenate a word if it's too long
        Returns (first_part, second_part)
        """
        if self.measure_text_width(word) <= max_width_inches:
            return word, ""

        # Simple hyphenation: break at syllables (rough approximation)
        for i in range(len(word) - 3, 2, -1):
            first_part = word[:i] + "-"
            if self.measure_text_width(first_part) <= max_width_inches:
                return first_part, word[i:]

        # If still too long, force break
        for i in range(len(word) - 1, 0, -1):
            first_part = word[:i] + "-"
            if self.measure_text_width(first_part) <= max_width_inches:
                return first_part, word[i:]

        return word, ""

    def calculate_height(self, num_lines: int, line_height_ratio: float = 1.2) -> float:
        """
        Calculate total height in inches for given number of lines
        """
        line_height_points = self.font_size * line_height_ratio
        return (num_lines * line_height_points) / 72.0
