"""
PDF Generation Service - Creates professional one-page resumes
Uses ReportLab for precise layout control
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

from app.schemas.resume import Resume
from app.services.one_page_engine import OnePageLayoutEngine


class PDFLayoutEngine:
    """
    Generates professional one-page PDF resumes with smart layout
    """
    
    # Default styling options
    DEFAULT_FONT = "Helvetica"
    DEFAULT_FONT_SIZE = 10
    DEFAULT_MARGINS = 0.5  # inches
    
    def __init__(
        self,
        page_size=letter,
        font_family: str = "Helvetica",
        font_size: int = 10,
        margins: float = 0.5,
        theme: str = "professional"
    ):
        self.page_size = page_size
        self.font_family = font_family
        self.font_size = font_size
        self.margins = margins * inch
        self.theme = theme
        
        # Calculate usable dimensions
        self.page_width, self.page_height = page_size
        self.content_width = self.page_width - (2 * self.margins)
        self.content_height = self.page_height - (2 * self.margins)
        
        # Theme colors
        self.colors = self._get_theme_colors(theme)
    
    def _get_theme_colors(self, theme: str) -> Dict[str, Any]:
        """Get color scheme for theme"""
        themes = {
            "professional": {
                "primary": colors.HexColor("#2c3e50"),
                "secondary": colors.HexColor("#34495e"),
                "accent": colors.HexColor("#3498db"),
                "text": colors.black,
                "light": colors.HexColor("#95a5a6")
            },
            "modern": {
                "primary": colors.HexColor("#1a237e"),
                "secondary": colors.HexColor("#303f9f"),
                "accent": colors.HexColor("#536dfe"),
                "text": colors.black,
                "light": colors.HexColor("#9fa8da")
            },
            "minimal": {
                "primary": colors.black,
                "secondary": colors.HexColor("#333333"),
                "accent": colors.HexColor("#555555"),
                "text": colors.black,
                "light": colors.HexColor("#999999")
            }
        }
        return themes.get(theme, themes["professional"])
    
    def generate_pdf(self, resume: Resume, output_path: Optional[Path] = None) -> BytesIO:
        """
        Generate ONE-PAGE PDF from Resume object
        Automatically adjusts spacing to fit content on a single page
        Uses OnePageLayoutEngine for intelligent compression
        Returns BytesIO buffer if no output_path specified
        """
        # Use one-page layout engine to calculate optimal settings
        layout_engine = OnePageLayoutEngine()
        # Convert Resume Pydantic model to dict
        try:
            resume_dict = resume.model_dump() if hasattr(resume, 'model_dump') else resume.dict()
        except:
            # Fallback: convert manually
            resume_dict = {
                "header": resume.header if isinstance(resume.header, dict) else resume.header.dict(),
                "summary": resume.summary,
                "experience": [exp.dict() if hasattr(exp, 'dict') else exp for exp in resume.experience],
                "projects": [proj.dict() if hasattr(proj, 'dict') else proj for proj in resume.projects],
                "skills": resume.skills,
                "education": [edu.dict() if hasattr(edu, 'dict') else edu for edu in resume.education],
            }
        metrics = layout_engine.calculate_layout(resume_dict, current_font_size=self.font_size)
        
        # Adjust font size and spacing based on layout engine recommendations
        if not metrics.fits_one_page:
            # Don't go below 8pt font for readability
            self.font_size = max(metrics.font_size, 8)
            # Adjust spacing based on compression level with improved limits
            compression_limits = {
                "aggressive": 0.5,   # Changed from 0.25 - less cramped
                "moderate": 0.65,    # Changed from 0.5
                "light": 0.8,        # Changed from 0.75
                "none": 1.0
            }
            spacing_multiplier = compression_limits.get(
                metrics.compression_level, 
                1.0
            )
        else:
            spacing_multiplier = 1.0

        buffer = BytesIO()

        # Try different spacing levels to fit content on one page (fallback)
        # Removed 0.35 and 0.25 to prevent overly cramped layouts
        spacing_multipliers = [spacing_multiplier, 0.8, 0.65, 0.5]

        for spacing in spacing_multipliers:
            buffer = BytesIO()

            # Create PDF document with single page constraint
            doc = SimpleDocTemplate(
                buffer if not output_path else str(output_path),
                pagesize=self.page_size,
                leftMargin=self.margins,
                rightMargin=self.margins,
                topMargin=self.margins,
                bottomMargin=self.margins,
                showBoundary=0
            )

            # Build content with current spacing
            story = []
            styles = self._create_styles()

            # Use structure metadata to determine section order if available
            if hasattr(resume, 'structure') and resume.structure and resume.structure.section_order:
                section_order = resume.structure.section_order
            else:
                # Default order if no structure metadata
                section_order = ["header", "summary", "experience", "projects", "education", "skills", "certifications", "awards"]

            # Section builder mapping
            section_builders = {
                "header": lambda: self._build_header(resume, styles),
                "summary": lambda: self._build_summary(resume, styles) if resume.summary else [],
                "experience": lambda: self._build_experience(resume, styles, spacing) if resume.experience else [],
                "projects": lambda: self._build_projects(resume, styles, spacing) if resume.projects else [],
                "education": lambda: self._build_education(resume, styles, spacing) if resume.education else [],
                "skills": lambda: self._build_skills(resume, styles) if resume.skills else [],
                "certifications": lambda: self._build_certifications(resume, styles, spacing) if hasattr(resume, 'certifications') and resume.certifications else [],
                "awards": lambda: self._build_awards(resume, styles, spacing) if hasattr(resume, 'awards') and resume.awards else []
            }

            # Build sections in the order they appeared in the original resume
            for i, section in enumerate(section_order):
                if section in section_builders:
                    section_content = section_builders[section]()
                    if section_content:  # Only add if content exists
                        story.extend(section_content)
                        # Add spacing between sections (except after last section)
                        if i < len(section_order) - 1:
                            if section == "header":
                                story.append(Spacer(1, 0.15 * inch * spacing))
                            else:
                                story.append(Spacer(1, 0.12 * inch * spacing))

            # Flexible sections (always at the end)
            if hasattr(resume, 'flexible_sections') and resume.flexible_sections:
                story.extend(self._build_flexible_sections(resume, styles, spacing))

            # Track page count
            page_count = [0]

            def on_page(canvas, doc):
                page_count[0] += 1

            # Build PDF
            try:
                doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

                # If it fits on one page, we're done
                if page_count[0] <= 1:
                    break
            except:
                # If build fails, try next spacing level
                continue

        if not output_path:
            buffer.seek(0)
            return buffer

        return buffer
    
    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles"""
        styles = {}
        
        # Name style
        styles['Name'] = ParagraphStyle(
            'Name',
            fontName=f'{self.font_family}-Bold',
            fontSize=self.font_size + 10,
            textColor=self.colors["primary"],
            alignment=TA_CENTER,
            spaceAfter=2
        )
        
        # Title style
        styles['Title'] = ParagraphStyle(
            'Title',
            fontName=self.font_family,
            fontSize=self.font_size + 2,
            textColor=self.colors["secondary"],
            alignment=TA_CENTER,
            spaceAfter=4
        )
        
        # Contact style
        styles['Contact'] = ParagraphStyle(
            'Contact',
            fontName=self.font_family,
            fontSize=self.font_size - 1,
            textColor=self.colors["text"],
            alignment=TA_CENTER,
            spaceAfter=6
        )
        
        # Section header
        styles['SectionHeader'] = ParagraphStyle(
            'SectionHeader',
            fontName=f'{self.font_family}-Bold',
            fontSize=self.font_size + 2,
            textColor=self.colors["primary"],
            spaceAfter=4,
            spaceBefore=2,
            borderPadding=2,
            borderColor=self.colors["accent"],
            borderWidth=0,
            borderRadius=0
        )
        
        # Job title
        styles['JobTitle'] = ParagraphStyle(
            'JobTitle',
            fontName=f'{self.font_family}-Bold',
            fontSize=self.font_size,
            textColor=self.colors["text"],
            spaceAfter=1
        )
        
        # Company
        styles['Company'] = ParagraphStyle(
            'Company',
            fontName=f'{self.font_family}-Oblique',
            fontSize=self.font_size - 1,
            textColor=self.colors["secondary"],
            spaceAfter=2
        )
        
        # Bullet
        styles['Bullet'] = ParagraphStyle(
            'Bullet',
            fontName=self.font_family,
            fontSize=self.font_size - 1,
            textColor=self.colors["text"],
            leftIndent=15,
            spaceAfter=3,
            bulletIndent=5
        )
        
        # Normal text
        styles['Normal'] = ParagraphStyle(
            'Normal',
            fontName=self.font_family,
            fontSize=self.font_size - 1,
            textColor=self.colors["text"],
            spaceAfter=4,
            alignment=TA_JUSTIFY
        )
        
        # Date (right-aligned) - NEW for better formatting
        styles['DateRight'] = ParagraphStyle(
            'DateRight',
            fontName=f'{self.font_family}-Oblique',
            fontSize=self.font_size - 1,
            textColor=self.colors["secondary"],
            alignment=TA_RIGHT,
            spaceAfter=2
        )
        
        return styles
    
    def _build_header(self, resume: Resume, styles: Dict) -> List:
        """Build header section with name, title, contact"""
        elements = []
        
        # Name
        name = resume.header.get("name", "")
        if name:
            elements.append(Paragraph(name, styles['Name']))
        
        # Title
        title = resume.header.get("title", "")
        if title:
            elements.append(Paragraph(title, styles['Title']))
        
        # Contact info
        contact = resume.header.get("contact", {})
        contact_parts = []
        
        if contact.get("email"):
            contact_parts.append(contact["email"])
        if contact.get("phone"):
            contact_parts.append(contact["phone"])
        if contact.get("location"):
            contact_parts.append(contact["location"])
        if contact.get("linkedin"):
            linkedin = contact["linkedin"]
            if not linkedin.startswith("http"):
                linkedin = f"linkedin.com/in/{linkedin}"
            contact_parts.append(linkedin)
        if contact.get("github"):
            github = contact["github"]
            if not github.startswith("http"):
                github = f"github.com/{github}"
            contact_parts.append(github)
        if contact.get("website"):
            contact_parts.append(contact["website"])
        
        if contact_parts:
            contact_text = " • ".join(contact_parts)
            elements.append(Paragraph(contact_text, styles['Contact']))
        
        return elements
    
    def _build_summary(self, resume: Resume, styles: Dict) -> List:
        """Build summary section"""
        elements = []
        elements.append(self._section_header("SUMMARY", styles))
        elements.append(Paragraph(resume.summary, styles['Normal']))
        return elements
    
    def _build_experience(self, resume: Resume, styles: Dict, spacing: float = 1.0) -> List:
        """Build experience section with right-aligned dates"""
        elements = []
        elements.append(self._section_header("EXPERIENCE", styles))

        for exp in resume.experience:
            # Prepare data for 2-row layout
            # Row 1: Title (Left) | Dates (Right)
            # Row 2: Company (Left) | Location (Right)
            
            # Row 1 Data
            title_text = f"<b>{exp.title}</b>"
            dates_text = ""
            if exp.start_date or exp.end_date:
                dates_text = exp.start_date or ""
                if exp.end_date:
                    dates_text += f" – {exp.end_date}"
                elif exp.current:
                    dates_text += " – Present"
            
            # Row 2 Data
            company_text = f"<i>{exp.company}</i>" if exp.company else ""
            location_text = f"<i>{exp.location}</i>" if exp.location else ""
            
            # Build Table Data
            data = []
            
            # Row 1
            data.append([
                Paragraph(title_text, styles['JobTitle']),
                Paragraph(dates_text, styles['DateRight'])
            ])
            
            # Row 2 (only if company or location exists)
            if company_text or location_text:
                data.append([
                    Paragraph(company_text, styles['Company']),
                    Paragraph(location_text, styles['DateRight'])
                ])
            
            col_widths = [self.content_width * 0.7, self.content_width * 0.3]
            
            table = Table(data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),   # Left column left-aligned
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Right column right-aligned
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(table)

            # Bullets with proper indentation
            for bullet in exp.bullets:
                if bullet.strip():
                    # Add bullet point
                    bullet_text = f"• {bullet}"
                    elements.append(Paragraph(bullet_text, styles['Bullet']))

            elements.append(Spacer(1, 0.08 * inch * spacing))

        return elements
    
    def _build_projects(self, resume: Resume, styles: Dict, spacing: float = 1.0) -> List:
        """Build projects section with right-aligned dates"""
        elements = []
        elements.append(self._section_header("PROJECTS", styles))

        for project in resume.projects:
            # Project name and URL for left side
            project_name = f"<b>{project.name}</b>"
            if project.url:
                project_name += f" | {project.url}"
            
            # Build dates for right side
            dates = ""
            if project.start_date or project.end_date:
                dates = project.start_date or ""
                if project.end_date:
                    dates += f" – {project.end_date}"
            
            # Create table with two columns for proper alignment
            if dates:
                data = [[
                    Paragraph(project_name, styles['JobTitle']),
                    Paragraph(dates, styles['DateRight'])
                ]]
                col_widths = [self.content_width * 0.68, self.content_width * 0.32]
                
                table = Table(data, colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ]))
                elements.append(table)
            else:
                # No dates, just regular paragraph
                elements.append(Paragraph(project_name, styles['JobTitle']))

            # Description
            if project.description:
                elements.append(Paragraph(project.description, styles['Company']))

            # Bullets
            for bullet in project.bullets:
                if bullet.strip():
                    bullet_text = f"• {bullet}"
                    elements.append(Paragraph(bullet_text, styles['Bullet']))

            # Technologies
            if project.technologies:
                tech_text = f"<i>Technologies: {', '.join(project.technologies)}</i>"
                elements.append(Paragraph(tech_text, styles['Company']))

            elements.append(Spacer(1, 0.08 * inch * spacing))

        return elements
    
    def _build_education(self, resume: Resume, styles: Dict, spacing: float = 1.0) -> List:
        """Build education section with right-aligned dates"""
        elements = []
        elements.append(self._section_header("EDUCATION", styles))

        for edu in resume.education:
            # Row 1: Institution (Left) | Dates (Right)
            # Row 2: Degree (Left) | Location (Right)
            
            # Row 1 Data
            inst_text = f"<b>{edu.institution}</b>"
            
            dates_text = ""
            if edu.end_date:
                dates_text = edu.end_date
            elif edu.start_date:
                dates_text = f"{edu.start_date} – Present"
                
            # Row 2 Data
            degree_text = f"<i>{edu.degree}</i>"
            if edu.field:
                degree_text += f" in {edu.field}"
            
            location_text = f"<i>{edu.location}</i>" if edu.location else ""
            if edu.gpa:
                if location_text:
                    location_text += f" | GPA: {edu.gpa}"
                else:
                    location_text = f"GPA: {edu.gpa}"

            # Build Table Data
            data = []
            
            # Row 1
            data.append([
                Paragraph(inst_text, styles['JobTitle']),
                Paragraph(dates_text, styles['DateRight'])
            ])
            
            # Row 2
            data.append([
                Paragraph(degree_text, styles['Company']),
                Paragraph(location_text, styles['DateRight'])
            ])
            
            col_widths = [self.content_width * 0.7, self.content_width * 0.3]
            
            table = Table(data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(table)

            # Honors
            if edu.honors:
                honors_text = f"<i>Honors: {', '.join(edu.honors)}</i>"
                elements.append(Paragraph(honors_text, styles['Bullet']))
                
            # Coursework
            if hasattr(edu, 'coursework') and edu.coursework:
                course_text = f"<i>Coursework: {', '.join(edu.coursework)}</i>"
                elements.append(Paragraph(course_text, styles['Bullet']))

            elements.append(Spacer(1, 0.05 * inch * spacing))

        return elements
    
    def _build_skills(self, resume: Resume, styles: Dict) -> List:
        """Build skills section"""
        elements = []
        elements.append(self._section_header("SKILLS", styles))
        
        for category, skills in resume.skills.items():
            if skills:
                skill_text = f"<b>{category}:</b> {', '.join(skills)}"
                elements.append(Paragraph(skill_text, styles['Normal']))
        
        return elements
    
    def _section_header(self, text: str, styles: Dict) -> Paragraph:
        """Create a section header with underline"""
        style = styles['SectionHeader']
        # Add underline using table
        return Paragraph(f"<u>{text}</u>", style)

    def _build_certifications(self, resume: Resume, styles: Dict, spacing: float = 1.0) -> List:
        """Build certifications section"""
        elements = []
        elements.append(self._section_header("CERTIFICATIONS", styles))

        for cert in resume.certifications:
            # Certification name
            cert_text = f"<b>{cert.name}</b>"
            if cert.issuer:
                cert_text += f" | {cert.issuer}"

            elements.append(Paragraph(cert_text, styles['JobTitle']))

            # Date and details
            details = []
            if cert.date:
                details.append(cert.date)
            if cert.expiry:
                details.append(f"Expires: {cert.expiry}")
            if cert.credential_id:
                details.append(f"ID: {cert.credential_id}")

            if details:
                elements.append(Paragraph(f"<i>{' | '.join(details)}</i>", styles['Company']))

            if cert.url:
                elements.append(Paragraph(f"<i>{cert.url}</i>", styles['Company']))

            elements.append(Spacer(1, 0.05 * inch * spacing))

        return elements

    def _build_awards(self, resume: Resume, styles: Dict, spacing: float = 1.0) -> List:
        """Build awards section"""
        elements = []
        elements.append(self._section_header("AWARDS & HONORS", styles))

        for award in resume.awards:
            # Award name
            award_text = f"<b>{award.name}</b>"
            if award.issuer:
                award_text += f" | {award.issuer}"
            if award.date:
                award_text += f" | {award.date}"

            elements.append(Paragraph(award_text, styles['JobTitle']))

            # Description
            if award.description:
                elements.append(Paragraph(award.description, styles['Normal']))

            elements.append(Spacer(1, 0.05 * inch * spacing))

        return elements

    def _build_flexible_sections(self, resume: Resume, styles: Dict, spacing: float = 1.0) -> List:
        """Build flexible sections (volunteer, publications, etc.)"""
        elements = []

        # Sort by order
        sorted_sections = sorted(resume.flexible_sections, key=lambda x: x.order)

        for section in sorted_sections:
            elements.append(Spacer(1, 0.12 * inch * spacing))
            elements.append(self._section_header(section.title.upper(), styles))

            # Handle different content types
            if isinstance(section.content, list):
                for item in section.content:
                    if isinstance(item, str):
                        elements.append(Paragraph(f"• {item}", styles['Bullet']))
                    elif isinstance(item, dict):
                        # Flexible dict format
                        if 'name' in item or 'title' in item:
                            title = item.get('name', item.get('title', ''))
                            elements.append(Paragraph(f"<b>{title}</b>", styles['JobTitle']))

                        if 'description' in item:
                            elements.append(Paragraph(item['description'], styles['Normal']))

                        if 'bullets' in item and isinstance(item['bullets'], list):
                            for bullet in item['bullets']:
                                elements.append(Paragraph(f"• {bullet}", styles['Bullet']))

            elif isinstance(section.content, str):
                elements.append(Paragraph(section.content, styles['Normal']))

            elements.append(Spacer(1, 0.05 * inch * spacing))

        return elements


class ResumePDFGenerator:
    """Main service for generating resume PDFs"""
    
    @staticmethod
    def generate(
        resume: Resume,
        output_path: Optional[Path] = None,
        font_family: str = "Helvetica",
        font_size: int = 10,
        theme: str = "professional"
    ) -> BytesIO:
        """
        Generate a professional one-page PDF resume
        
        Args:
            resume: Resume object with structured data
            output_path: Optional path to save PDF
            font_family: Font to use (Helvetica, Times, Courier)
            font_size: Base font size in points
            theme: Color theme (professional, modern, minimal)
        
        Returns:
            BytesIO buffer containing PDF
        """
        engine = PDFLayoutEngine(
            font_family=font_family,
            font_size=font_size,
            theme=theme
        )
        
        return engine.generate_pdf(resume, output_path)
