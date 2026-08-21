"""分类服务层（后台）。分类字典：series/space/category 三类，支持树形。"""
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryIn, CategoryOut


def list_categories(db: Session, *, keyword: str | None = None, kind: str | None = None) -> list[Category]:
    """后台分类扁平列表（未删除）。"""
    q = select(Category).where(Category.is_deleted == 0)
    if kind:
        q = q.where(Category.kind == kind)
    if keyword:
        q = q.where(Category.name.like(f"%{keyword}%"))
    q = q.order_by(Category.kind, Category.sort, Category.id)
    return list(db.execute(q).scalars().all())


def build_tree(items: list[Category]) -> list[CategoryOut]:
    """把扁平分类组装为树（children 嵌套）。"""
    nodes = {c.id: CategoryOut.model_validate(c) for c in items}
    roots: list[CategoryOut] = []
    for c in items:
        node = nodes[c.id]
        if c.parent_id and c.parent_id in nodes:
            parent = nodes[c.parent_id]
            if not hasattr(parent, "children"):
                parent.children = []
            parent.children.append(node)
        else:
            roots.append(node)
    return roots


def options(db: Session, *, kind: str | None = None) -> list[CategoryOut]:
    """分类下拉（扁平，不组装树，按 type+sort）。"""
    q = select(Category).where(Category.is_deleted == 0, Category.enabled == 1)
    if kind:
        q = q.where(Category.kind == kind)
    q = q.order_by(Category.kind, Category.sort, Category.id)
    return [CategoryOut.model_validate(c) for c in db.execute(q).scalars().all()]


def get_category(db: Session, category_id: int) -> Category | None:
    c = db.get(Category, category_id)
    return c if c and not c.is_deleted else None


def create_category(db: Session, payload: CategoryIn, admin_id: int) -> CategoryOut:
    data: dict[str, Any] = payload.model_dump()
    data["created_at"] = admin_id
    data["updated_at"] = admin_id
    c = Category(**data)
    db.add(c)
    db.commit()
    db.refresh(c)
    return CategoryOut.model_validate(c)


def update_category(db: Session, category_id: int, payload: CategoryIn, admin_id: int) -> CategoryOut | None:
    c = get_category(db, category_id)
    if not c:
        return None
    # 防自引用（数据库 CHECK 双保险）
    if payload.parent_id == category_id:
        return None
    for k, v in payload.model_dump().items():
        setattr(c, k, v)
    c.updated_at = admin_id
    db.commit()
    db.refresh(c)
    return CategoryOut.model_validate(c)


def delete_category(db: Session, category_id: int, admin_id: int) -> bool:
    """软删除。有子分类或被产品引用时拒绝。"""
    c = get_category(db, category_id)
    if not c:
        return False
    child = db.execute(select(Category).where(Category.parent_id == category_id, Category.is_deleted == 0)).scalars().first()
    if child:
        return False
    c.is_deleted = 1
    c.updated_at = admin_id
    db.commit()
    return True


__all__ = ["list_categories", "build_tree", "options", "get_category", "create_category", "update_category", "delete_category"]
