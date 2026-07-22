"""Template management API routes."""

import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse, TemplateVersionResponse
from app.models.template import Template, TemplateStatus, TemplateVersion
from app.models.user import User
from app.api.deps import get_current_user
from app.services.storage import template_storage
from app.core.config import settings

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.post("", response_model=TemplateResponse, status_code=201)
def upload_template(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(""),
    category: str = Form(""),
    tags: str = Form("[]"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a new Word template."""
    if not file.filename or not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="仅支持 .docx 格式的模板文件")

    # Validate file size
    content = file.file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制 (50MB)")

    # Save file
    import json
    tags_list = json.loads(tags)
    file_path = template_storage.save("", file.filename, content)

    # Create template record
    template = Template(
        name=name,
        description=description,
        category=category,
        tags=tags_list,
        status=TemplateStatus.DRAFT,
        file_path=file_path,
        created_by=current_user.id,
    )
    db.add(template)
    db.commit()
    db.refresh(template)

    # Create initial version
    version = TemplateVersion(
        template_id=template.id,
        version_number=1,
        file_path=file_path,
        change_description="初始版本",
        created_by=current_user.id,
    )
    db.add(version)
    db.commit()

    return template


@router.get("", response_model=list[TemplateResponse])
def list_templates(
    category: str | None = Query(None),
    search: str | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List templates with optional filtering."""
    query = db.query(Template)

    if category:
        query = query.filter(Template.category == category)
    if status:
        query = query.filter(Template.status == status)
    if search:
        query = query.filter(Template.name.ilike(f"%{search}%"))

    return query.order_by(Template.updated_at.desc()).all()


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get template details."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: str,
    update: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update template metadata or status."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(template, key, value)
    template.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=204)
def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a template."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    db.delete(template)
    db.commit()


@router.get("/{template_id}/versions", response_model=list[TemplateVersionResponse])
def get_template_versions(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get version history for a template."""
    return db.query(TemplateVersion).filter(
        TemplateVersion.template_id == template_id
    ).order_by(TemplateVersion.version_number.desc()).all()


@router.post("/{template_id}/versions/{version_id}/rollback", response_model=TemplateResponse)
def rollback_template(
    template_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rollback template to a previous version."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    version = db.query(TemplateVersion).filter(
        TemplateVersion.id == version_id,
        TemplateVersion.template_id == template_id,
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")

    # Create new version from the rollback target
    new_version = TemplateVersion(
        template_id=template_id,
        version_number=template.current_version + 1,
        file_path=version.file_path,
        change_description=f"回滚至版本 {version.version_number}",
        created_by=current_user.id,
    )
    template.file_path = version.file_path
    template.current_version += 1
    db.add(new_version)
    db.commit()
    db.refresh(template)
    return template
