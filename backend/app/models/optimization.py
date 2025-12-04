"""
Optimization Session Model
"""
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base


class OptimizationStatus(str, enum.Enum):
    """Optimization session status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class OptimizationSession(Base):
    """Optimization session for resume tailoring"""

    __tablename__ = "optimization_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(String, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_description_id = Column(String, ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True, index=True)

    # Status
    status = Column(SQLEnum(OptimizationStatus), default=OptimizationStatus.PENDING, nullable=False)

    # Input
    original_resume = Column(JSON, nullable=False)  # Snapshot of resume at optimization time
    target_job = Column(JSON, nullable=True)  # Job description data

    # Analysis results
    match_score = Column(Float, nullable=True)  # 0.0 - 1.0
    analysis = Column(JSON, nullable=True)
    # Contains: missing_keywords, strengths, weaknesses, recommendations

    # Optimized output
    optimized_resume = Column(JSON, nullable=True)
    changes_made = Column(JSON, nullable=True)  # List of changes applied

    # Error handling
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="optimization_sessions")
    resume = relationship("Resume", back_populates="optimization_sessions")
    job_description = relationship("JobDescription", back_populates="optimization_sessions")

    def __repr__(self):
        return f"<OptimizationSession {self.id} - {self.status}>"
