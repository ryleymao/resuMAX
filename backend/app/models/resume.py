"""
Resume Models
"""
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Integer, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Resume(Base):
    """Resume model - stores canonical resume data"""

    __tablename__ = "resumes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Basic info
    name = Column(String, nullable=False)  # Resume name (e.g., "Software Engineer Resume")
    original_filename = Column(String, nullable=True)

    # Canonical JSON (single source of truth)
    canonical_data = Column(JSON, nullable=False)

    # Metadata
    file_path = Column(String, nullable=True)  # Original file path in storage
    storage_url = Column(String, nullable=True)  # URL to stored file

    # Version control
    version = Column(Integer, default=1, nullable=False)
    is_latest = Column(Boolean, default=True, nullable=False)

    # Layout configuration
    layout_config = Column(JSON, nullable=True)  # User's layout preferences

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="resumes")
    versions = relationship("ResumeVersion", back_populates="resume", cascade="all, delete-orphan")
    optimization_sessions = relationship("OptimizationSession", back_populates="resume", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Resume {self.name} (v{self.version})>"


class ResumeVersion(Base):
    """Resume version history"""

    __tablename__ = "resume_versions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)

    # Version info
    version_number = Column(Integer, nullable=False)
    change_description = Column(Text, nullable=True)

    # Snapshot of canonical data at this version
    canonical_data = Column(JSON, nullable=False)
    layout_config = Column(JSON, nullable=True)

    # Generated outputs
    pdf_url = Column(String, nullable=True)
    docx_url = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=True)  # User ID or "system" for auto-versions

    # Relationships
    resume = relationship("Resume", back_populates="versions")

    def __repr__(self):
        return f"<ResumeVersion {self.resume_id} v{self.version_number}>"
