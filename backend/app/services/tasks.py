"""Celery tasks for document generation and processing."""

import os
import uuid
from datetime import datetime

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.task import BatchTask, BatchTaskStatus, BatchTaskItem
from app.models.document import Document, DocumentStatus
from app.models.template import Template
from app.services.storage import template_storage, document_storage
from engine.app.core.renderer import generate_document


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_batch_task(self, task_id: str):
    """Process a batch generation task asynchronously."""
    db = SessionLocal()
    try:
        task = db.query(BatchTask).filter(BatchTask.id == task_id).first()
        if not task:
            return {"error": "Task not found"}

        template = db.query(Template).filter(Template.id == task.template_id).first()
        if not template:
            task.status = BatchTaskStatus.FAILED
            db.commit()
            return {"error": "Template not found"}

        items = db.query(BatchTaskItem).filter(
            BatchTaskItem.task_id == task_id,
            BatchTaskItem.status == BatchTaskStatus.PENDING,
        ).all()

        template_path = template_storage.get_full_path(template.file_path)
        completed = 0
        failed = 0

        for item in items:
            try:
                item.status = BatchTaskStatus.PROCESSING
                db.commit()

                # Generate document
                output_filename = f"{uuid.uuid4().hex}.docx"
                output_rel_path = document_storage.save("batch", output_filename, b"")
                output_full_path = document_storage.get_full_path(output_rel_path)

                generate_document(template_path, item.input_data, output_full_path)

                # Create document record
                doc = Document(
                    title=f"{task.title}_第{item.row_index + 1}份",
                    template_id=template.id,
                    template_version=template.current_version,
                    status=DocumentStatus.DRAFT,
                    variable_values=item.input_data,
                    file_path=output_rel_path,
                    created_by=task.created_by,
                    batch_task_id=task.id,
                )
                db.add(doc)
                db.flush()

                item.document_id = doc.id
                item.status = BatchTaskStatus.COMPLETED
                completed += 1
                db.commit()

            except Exception as e:
                item.status = BatchTaskStatus.FAILED
                item.error_message = str(e)
                failed += 1
                db.commit()

        task.completed_count = completed
        task.failed_count = failed
        if failed > 0 and completed == 0:
            task.status = BatchTaskStatus.FAILED
        else:
            task.status = BatchTaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        db.commit()

        return {"completed": completed, "failed": failed}

    except Exception as e:
        task = db.query(BatchTask).filter(BatchTask.id == task_id).first()
        if task:
            task.status = BatchTaskStatus.FAILED
            db.commit()
        raise self.retry(exc=e)
    finally:
        db.close()
