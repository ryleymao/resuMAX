"""
Layout Models
"""
from sqlalchemy import Column, String, JSON, DateTime, Boolean, Text
from datetime import datetime
import uuid
from app.core.database import Base


class LayoutTemplate(Base):
    """Layout template definitions"""

    __tablename__ = "layout_templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Template info
    name = Column(String, unique=True, nullable=False, index=True)  # e.g., "modern_tech"
    display_name = Column(String, nullable=False)  # e.g., "Modern Tech Resume"
    description = Column(Text, nullable=True)

    # Template configuration
    config = Column(JSON, nullable=False)  # Default template settings

    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    preview_image_url = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<LayoutTemplate {self.display_name}>"


class LayoutConfiguration(Base):
    """User-specific layout configurations"""

    __tablename__ = "layout_configurations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)  # Reference to user

    # Configuration
    name = Column(String, nullable=False)  # User-defined name
    template_name = Column(String, nullable=False)  # Base template
    config = Column(JSON, nullable=False)  # Custom overrides

    # Metadata
    is_default = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<LayoutConfiguration {self.name}>"
