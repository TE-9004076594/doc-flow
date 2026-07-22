"""Template variable model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, JSON, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class TemplateVariable(Base):
    __tablename__ = "template_variables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    label = Column(String(200))
    var_type = Column(String(50), nullable=False, default="text")  # text, number, date, enum, boolean, object, list
    default_value = Column(Text)
    description = Column(Text)
    enum_options = Column(JSON)  # For enum type variables
    is_required = Column(Boolean, default=False)
    max_length = Column(Integer, nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    template = relationship("Template", back_populates="variables")
