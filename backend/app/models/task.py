"""Batch task and task item models."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class BatchTaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchTask(Base):
    __tablename__ = "batch_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500))
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    status = Column(Enum(BatchTaskStatus), default=BatchTaskStatus.PENDING, nullable=False)
    total_count = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    source_file = Column(String(500))  # Original import file path
    field_mapping = Column(JSON, default=dict)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    documents = relationship("Document", back_populates="batch_task")
    items = relationship("BatchTaskItem", back_populates="task", cascade="all, delete-orphan")


class BatchTaskItem(Base):
    __tablename__ = "batch_task_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("batch_tasks.id"), nullable=False, index=True)
    row_index = Column(Integer, nullable=False)
    input_data = Column(JSON, default=dict)
    status = Column(Enum(BatchTaskStatus), default=BatchTaskStatus.PENDING, nullable=False)
    error_message = Column(Text)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("BatchTask", back_populates="items")
