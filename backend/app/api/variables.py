"""Template variable API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.core.database import get_db
from app.models.template import Template
from app.models.variable import TemplateVariable
from app.models.user import User
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/templates/{template_id}/variables", tags=["variables"])


class VariableCreate(BaseModel):
    name: str
    label: str | None = None
    var_type: str = "text"
    default_value: str | None = None
    description: str | None = None
    enum_options: list[str] | None = None
    is_required: bool = False
    max_length: int | None = None
    sort_order: int = 0


class VariableUpdate(BaseModel):
    label: str | None = None
    var_type: str | None = None
    default_value: str | None = None
    description: str | None = None
    enum_options: list[str] | None = None
    is_required: bool | None = None
    max_length: int | None = None
    sort_order: int | None = None


@router.get("")
def list_variables(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all variables for a template."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template.variables


@router.put("")
def update_variables(
    template_id: str,
    variables: list[VariableCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Replace all variables for a template (bulk update)."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # Delete existing variables
    db.query(TemplateVariable).filter(TemplateVariable.template_id == template_id).delete()

    # Create new variables
    for i, var in enumerate(variables):
        tv = TemplateVariable(
            template_id=template_id,
            name=var.name,
            label=var.label or var.name,
            var_type=var.var_type,
            default_value=var.default_value,
            description=var.description,
            enum_options=var.enum_options,
            is_required=var.is_required,
            max_length=var.max_length,
            sort_order=var.sort_order or i,
        )
        db.add(tv)

    db.commit()
    return db.query(TemplateVariable).filter(TemplateVariable.template_id == template_id).all()
