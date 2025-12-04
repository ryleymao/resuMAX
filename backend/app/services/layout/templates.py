"""
Resume Layout Templates

Each template takes canonical JSON and produces a layout using primitives.
Templates are user-selectable and deterministic.
"""
from typing import Dict, Any, List
from .primitives import Block, Row, Column, Text, BulletList


class ResumeTemplate:
    """Base class for resume templates"""

    def __init__(self):
        self.page_width = 8.5  # inches
        self.page_height = 11.0  # inches
        self.margin_top = 0.5
        self.margin_bottom = 0.5
        self.margin_left = 0.75
        self.margin_right = 0.75

    def render(self, canonical: Dict[str, Any]) -> Block:
        """
        Convert canonical JSON to layout primitives
        Returns root Block containing entire resume
        """
        raise NotImplementedError


class ModernTechTemplate(ResumeTemplate):
    """
    Template A: Modern Tech
    - Configurable job headers (two-column or stacked)
    - Compact spacing
    - Configurable date alignment
    - Professional look
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.section_spacing = 0.15  # inches between sections
        self.entry_spacing = 0.12  # inches between entries
        self.bullet_spacing = 0.05  # inches between bullets

        # User-configurable options
        self.config = config or {}
        self.use_two_column_header = self.config.get("use_two_column_header", True)  # Default: two columns
        self.date_alignment = self.config.get("date_alignment", "right")  # Options: "right", "left", "inline"

    def render(self, canonical: Dict[str, Any]) -> Block:
        """Render resume using Modern Tech template"""
        sections = []

        # Header
        sections.append(self._render_header(canonical.get("header", {})))

        # Summary (if exists)
        if canonical.get("summary"):
            sections.append(self._render_summary(canonical["summary"]))

        # Skills (render first for visibility)
        if canonical.get("skills"):
            sections.append(self._render_skills(canonical["skills"]))

        # Experience
        if canonical.get("experience"):
            sections.append(self._render_experience(canonical["experience"]))

        # Projects
        if canonical.get("projects"):
            sections.append(self._render_projects(canonical["projects"]))

        # Education
        if canonical.get("education"):
            sections.append(self._render_education(canonical["education"]))

        return Block(children=sections)

    def _render_header(self, header: Dict[str, Any]) -> Block:
        """Render header with name and contact info"""
        elements = []

        # Name (large, bold, centered)
        if header.get("name"):
            elements.append(Text(
                content=header["name"],
                font_size=16.0,
                is_bold=True
            ))

        # Contact info (one line, centered)
        contact_parts = []
        for key in ["email", "phone", "linkedin", "github", "website"]:
            if header.get(key):
                contact_parts.append(header[key])

        if contact_parts:
            elements.append(Text(
                content=" • ".join(contact_parts),
                font_size=9.0
            ))

        return Block(children=elements, margin_bottom=self.section_spacing)

    def _render_skills(self, skills: Dict[str, List[str]]) -> Block:
        """Render skills section"""
        elements = []

        # Section title
        elements.append(Text(
            content="SKILLS",
            font_size=11.0,
            is_bold=True
        ))

        # Skills by category
        for category, skill_list in skills.items():
            if skill_list:
                # Category: Skills
                elements.append(Text(
                    content=f"{category}: {', '.join(skill_list)}",
                    font_size=10.0
                ))

        return Block(children=elements, margin_bottom=self.section_spacing)

    def _render_experience(self, experience: List[Dict[str, Any]]) -> Block:
        """Render experience section with configurable layout"""
        elements = []

        # Section title
        elements.append(Text(
            content="EXPERIENCE",
            font_size=11.0,
            is_bold=True
        ))

        for entry in experience:
            if self.use_two_column_header:
                # Two-column layout: Company/Title (left) | Location/Dates (right)
                left_col = Column(
                    width="70%",
                    align="left",
                    children=[
                        Text(content=entry.get("company", ""), font_size=10.0, is_bold=True),
                        Text(content=entry.get("title", ""), font_size=10.0, is_italic=True)
                    ]
                )

                # Build right column content
                right_content = []
                if entry.get("location"):
                    right_content.append(entry["location"])
                date_range = self._format_date_range(entry.get("start_date", ""), entry.get("end_date", ""))
                if date_range:
                    right_content.append(date_range)

                right_col = Column(
                    width="30%",
                    align=self.date_alignment,  # Configurable alignment
                    children=[Text(content=line, font_size=10.0) for line in right_content]
                )

                row = Row(columns=[left_col, right_col], margin_bottom=0.05)
                elements.append(row)
            else:
                # Stacked layout: everything left-aligned
                elements.append(Text(content=entry.get("company", ""), font_size=10.0, is_bold=True))

                # Title with optional inline date
                if self.date_alignment == "inline":
                    title_line = entry.get("title", "")
                    date_range = self._format_date_range(entry.get("start_date", ""), entry.get("end_date", ""))
                    if date_range:
                        title_line += f" | {date_range}"
                    elements.append(Text(content=title_line, font_size=10.0, is_italic=True))
                else:
                    elements.append(Text(content=entry.get("title", ""), font_size=10.0, is_italic=True))
                    if entry.get("location") or entry.get("start_date"):
                        location_date = []
                        if entry.get("location"):
                            location_date.append(entry["location"])
                        date_range = self._format_date_range(entry.get("start_date", ""), entry.get("end_date", ""))
                        if date_range:
                            location_date.append(date_range)
                        elements.append(Text(content=" • ".join(location_date), font_size=10.0))

            # Bullets
            if entry.get("bullets"):
                elements.append(BulletList(
                    bullets=entry["bullets"],
                    indent=0.25,
                    spacing=self.bullet_spacing,
                    font_size=10.0
                ))

            # Spacing after entry
            elements.append(Block(children=[], margin_bottom=self.entry_spacing))

        return Block(children=elements, margin_bottom=self.section_spacing)

    def _render_projects(self, projects: List[Dict[str, Any]]) -> Block:
        """Render projects section"""
        elements = []

        # Section title
        elements.append(Text(
            content="PROJECTS",
            font_size=11.0,
            is_bold=True
        ))

        for project in projects:
            # Project name (bold)
            if project.get("name"):
                elements.append(Text(
                    content=project["name"],
                    font_size=10.0,
                    is_bold=True
                ))

            # Bullets
            if project.get("bullets"):
                elements.append(BulletList(
                    bullets=project["bullets"],
                    indent=0.25,
                    spacing=self.bullet_spacing,
                    font_size=10.0
                ))

            # Spacing after project
            elements.append(Block(children=[], margin_bottom=self.entry_spacing))

        return Block(children=elements, margin_bottom=self.section_spacing)

    def _render_education(self, education: List[Dict[str, Any]]) -> Block:
        """Render education section"""
        elements = []

        # Section title
        elements.append(Text(
            content="EDUCATION",
            font_size=11.0,
            is_bold=True
        ))

        for entry in education:
            # Two-column: School/Degree (left) | Location/Date (right)
            left_col = Column(
                width="70%",
                align="left",
                children=[
                    Text(content=entry.get("institution", ""), font_size=10.0, is_bold=True),
                    Text(content=entry.get("degree", ""), font_size=10.0)
                ]
            )

            right_content = []
            if entry.get("location"):
                right_content.append(entry["location"])
            if entry.get("end_date"):
                right_content.append(entry["end_date"])

            right_col = Column(
                width="30%",
                align="right",
                children=[Text(content=line, font_size=10.0) for line in right_content]
            )

            row = Row(columns=[left_col, right_col])
            elements.append(row)

        return Block(children=elements, margin_bottom=self.section_spacing)

    def _render_summary(self, summary: str) -> Block:
        """Render summary section"""
        return Block(
            children=[
                Text(content="SUMMARY", font_size=11.0, is_bold=True),
                Text(content=summary, font_size=10.0)
            ],
            margin_bottom=self.section_spacing
        )

    def _format_date_range(self, start: str, end: str) -> str:
        """Format date range"""
        if not start:
            return ""
        if not end:
            return start
        return f"{start} - {end}"


class MinimalistTemplate(ResumeTemplate):
    """
    Template B: Minimalist
    - Everything left-aligned
    - Stacked job titles (no columns)
    - Wider margins
    - Clean, simple look
    """

    def __init__(self):
        super().__init__()
        self.margin_left = 1.0
        self.margin_right = 1.0
        self.section_spacing = 0.20
        self.entry_spacing = 0.15

    def render(self, canonical: Dict[str, Any]) -> Block:
        """Render using minimalist template"""
        # Similar to ModernTech but all left-aligned, no Row splits
        # (Implementation omitted for brevity - follows same pattern)
        pass


class ATSSafeTemplate(ResumeTemplate):
    """
    Template C: ATS Safe
    - No columns (everything stacked vertically)
    - Simple left-aligned text blocks
    - Maximum ATS compatibility
    - No fancy formatting
    """

    def __init__(self):
        super().__init__()
        self.section_spacing = 0.15
        self.entry_spacing = 0.10

    def render(self, canonical: Dict[str, Any]) -> Block:
        """Render using ATS-safe template"""
        # All text stacked vertically, no Row primitives
        # (Implementation omitted for brevity - follows same pattern)
        pass


# Template registry
TEMPLATES = {
    "modern_tech": ModernTechTemplate,
    "minimalist": MinimalistTemplate,
    "ats_safe": ATSSafeTemplate
}
