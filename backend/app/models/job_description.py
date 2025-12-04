"""
Job Description Model
"""
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class JobDescription(Base):
    """Job description for resume optimization"""

    __tablename__ = "job_descriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Job info
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    job_type = Column(String, nullable=True)  # full-time, part-time, contract, etc.

    # Raw job description
    raw_description = Column(Text, nullable=False)

    # Parsed/analyzed data (from LLM)
    parsed_data = Column(JSON, nullable=True)
    # Contains: required_skills, preferred_skills, responsibilities, qualifications, keywords

    # Metadata
    source_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="job_descriptions")
    optimization_sessions = relationship("OptimizationSession", back_populates="job_description")

    def __repr__(self):
        return f"<JobDescription {self.title} at {self.company}>"
