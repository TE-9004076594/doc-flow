"""Batch task management API routes."""

import json
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.template import Template, TemplateStatus
from app.models.document import Document, DocumentStatus
from app.models.task import BatchTask, BatchTaskStatus, BatchTaskItem
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/batch")
def create_batch_task(
    template_id: str = Query(...),
    title: str = Query("批量生成"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new batch generation task (accepts import file separately)."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    task = BatchTask(
        title=title,
        template_id=template.id,
        created_by=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"id": str(task.id), "status": task.status.value, "title": task.title}


@router.post("/batch/{task_id}/import")
def import_batch_data(
    task_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Import Excel/CSV data for a batch task."""
    import pandas as pd
    import io

    task = db.query(BatchTask).filter(BatchTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    content = file.file.read()
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else ""

    try:
        if ext in ("xlsx", "xls"):
            df = pd.read_excel(io.BytesIO(content))
        elif ext == "csv":
            df = pd.read_csv(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="仅支持 Excel (.xlsx/.xls) 或 CSV 文件")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")

    # Create task items
    for idx, row in df.iterrows():
        item = BatchTaskItem(
            task_id=task.id,
            row_index=idx,
            input_data=row.to_dict(),
        )
        db.add(item)

    task.total_count = len(df)
    db.commit()

    return {
        "task_id": task_id,
        "total_rows": task.total_count,
        "columns": list(df.columns),
    }


@router.get("")
def list_batch_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all batch tasks."""
    return db.query(BatchTask).filter(
        BatchTask.created_by == current_user.id
    ).order_by(BatchTask.created_at.desc()).all()


@router.get("/{task_id}")
def get_batch_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get batch task details with item status."""
    task = db.query(BatchTask).filter(BatchTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    items = db.query(BatchTaskItem).filter(BatchTaskItem.task_id == task_id).all()
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status.value,
        "total_count": task.total_count,
        "completed_count": task.completed_count,
        "failed_count": task.failed_count,
        "items": [
            {"row": i.row_index, "status": i.status.value, "error": i.error_message}
            for i in items
        ],
    }


@router.post("/{task_id}/start")
def start_batch_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start processing a batch task."""
    task = db.query(BatchTask).filter(BatchTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task.status = BatchTaskStatus.PROCESSING
    db.commit()

    # In MVP, processing is synchronous/simplified
    # V1 will use Celery for async processing
    from app.core.celery_app import celery_app

    celery_app.send_task("process_batch_task", args=[task_id])

    return {"status": "processing", "task_id": task_id}


@router.post("/{task_id}/cancel")
def cancel_batch_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a running batch task."""
    task = db.query(BatchTask).filter(BatchTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task.status = BatchTaskStatus.CANCELLED
    task.completed_at = datetime.utcnow()
    db.commit()
    return {"status": "cancelled"}


@router.post("/{task_id}/retry")
def retry_failed_items(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retry failed items in a batch task."""
    task = db.query(BatchTask).filter(BatchTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    failed_items = db.query(BatchTaskItem).filter(
        BatchTaskItem.task_id == task_id,
        BatchTaskItem.status == BatchTaskStatus.FAILED,
    ).all()

    for item in failed_items:
        item.status = BatchTaskStatus.PENDING
        item.error_message = None

    task.status = BatchTaskStatus.PROCESSING
    task.failed_count = 0
    db.commit()

    return {"retry_count": len(failed_items)}
