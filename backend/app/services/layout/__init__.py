"""
Grid-Based Layout System for Resume Rendering

Similar to professional ATS systems (Greenhouse, Lever, Workday).
Separates semantic content (canonical JSON) from presentation (layout templates).
"""
from .engine import LayoutEngine
from .primitives import Block, Row, Column, Text, BulletList
from .templates import TEMPLATES

__all__ = ["LayoutEngine", "Block", "Row", "Column", "Text", "BulletList", "TEMPLATES"]
