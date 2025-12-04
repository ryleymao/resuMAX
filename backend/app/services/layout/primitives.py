"""
Layout Primitives for Grid-Based Resume Rendering

These primitives allow deterministic layout without storing formatting in JSON.
Similar to how professional ATS systems (Greenhouse, Lever, Workday) render resumes.
"""
from dataclasses import dataclass
from typing import List, Literal, Union


@dataclass
class Text:
    """
    Text primitive with font metrics
    """
    content: str
    font_size: float = 10.0
    is_bold: bool = False
    is_italic: bool = False
    color: str = "#000000"


@dataclass
class Column:
    """
    Column in a Row
    width: percentage or pixels (e.g., "70%" or "400px")
    align: text alignment within column
    children: list of Text or Block elements
    """
    width: str  # "70%", "30%", "400px", etc.
    align: Literal["left", "center", "right"] = "left"
    children: List[Union[Text, 'Block']] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


@dataclass
class Row:
    """
    Horizontal grouping of columns
    """
    columns: List[Column]
    spacing: float = 0.1  # Space between columns in inches
    margin_bottom: float = 0.0  # Space after row


@dataclass
class Block:
    """
    Vertical stack of items (Rows or Text)
    """
    children: List[Union[Row, Text, 'Block']]
    margin_top: float = 0.0
    margin_bottom: float = 0.0
    indent: float = 0.0  # Left indent in inches

    def __post_init__(self):
        if not isinstance(self.children, list):
            self.children = [self.children]


@dataclass
class BulletList:
    """
    Special block for bullet points
    """
    bullets: List[str]
    bullet_char: str = "•"
    indent: float = 0.25  # Indent from left margin
    spacing: float = 0.05  # Space between bullets
    font_size: float = 10.0
