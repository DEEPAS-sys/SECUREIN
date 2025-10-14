from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.db.session import get_db
from app.models.db_models import Rule
from app.models.pydantic_schemas import RuleCreate, RuleUpdate, RuleResponse
from app.core.security import get_current_user, require_role

router = APIRouter()


@router.post("/", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_data: RuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("operator"))
):
    """Create a new rule"""
    
    new_rule = Rule(
        camera_id=rule_data.camera_id,
        name=rule_data.name,
        type=rule_data.type,
        rule_config=rule_data.rule_config,
        enabled=rule_data.enabled
    )
    
    db.add(new_rule)
    await db.commit()
    await db.refresh(new_rule)
    
    return new_rule


@router.get("/", response_model=List[RuleResponse])
async def list_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    camera_id: Optional[int] = None,
    enabled: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all rules"""
    
    query = select(Rule)
    
    if camera_id:
        query = query.where(Rule.camera_id == camera_id)
    if enabled is not None:
        query = query.where(Rule.enabled == enabled)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    rules = result.scalars().all()
    
    return rules


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get rule details"""
    
    result = await db.execute(
        select(Rule).where(Rule.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    return rule


@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: int,
    rule_data: RuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("operator"))
):
    """Update a rule"""
    
    result = await db.execute(
        select(Rule).where(Rule.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    # Update fields
    update_data = rule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    await db.commit()
    await db.refresh(rule)
    
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("operator"))
):
    """Delete a rule"""
    
    result = await db.execute(
        select(Rule).where(Rule.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    await db.delete(rule)
    await db.commit()
    
    return None
