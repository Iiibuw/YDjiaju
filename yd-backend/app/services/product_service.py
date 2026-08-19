"""产品服务层。前台公开读 + 后台 CRUD（M1 范围）。"""
import json
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductDetail, ProductListItem


# ===== 公共读（前台） =====

def _cents_to_yuan(min_c: int | None, max_c: int | None) -> str | None:
    if min_c is None and max_c is None:
        return None
    if min_c is not None and max_c is None:
        return f"¥{min_c / 100:.2f}"
    if min_c is None and max_c is not None:
        return f"¥{max_c / 100:.2f}"
    if min_c == max_c:
        return f"¥{min_c / 100:.2f}"
    return f"¥{min_c / 100:.2f} – ¥{max_c / 100:.2f}"


def list_products(
    db: Session,
    *,
    category_id: int | None = None,
    space_id: int | None = None,
    series_id: int | None = None,
    keyword: str | None = None,
    is_top: int | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ProductListItem], int]:
    """前台产品列表：仅返回 status='on_sale' 的可见产品（M1 简化）。"""
    q = select(Product).where(Product.status == "on_sale", Product.is_deleted == 0)
    if category_id:
        q = q.where(Product.category_id == category_id)
    if space_id:
        q = q.where(Product.space_id == space_id)
    if series_id:
        q = q.where(Product.series_id == series_id)
    if is_top is not None:
        q = q.where(Product.is_top == is_top)
    # 关键词：M1 用 LIKE（M2 改 FULLTEXT ngram）
    if keyword:
        like = f"%{keyword}%"
        q = q.where(Product.name.like(like))

    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    q = q.order_by(Product.is_top.desc(), Product.sort.asc(), Product.id.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(q).all()

    items: list[ProductListItem] = []
    for p in rows:
        items.append(
            ProductListItem(
                id=p.id,
                product_code=p.product_code,
                name=p.name,
                subtitle=p.subtitle,
                cover_url=p.cover_url,
                min_price_cents=p.min_price_cents,
                max_price_cents=p.max_price_cents,
                price_yuan=_cents_to_yuan(p.min_price_cents, p.max_price_cents),
                is_top=p.is_top,
                status=p.status,
                category_id=p.category_id,
                series_id=p.series_id,
                space_id=p.space_id,
            )
        )
    return items, total


def get_product_detail(db: Session, product_id: int) -> ProductDetail | None:
    """前台产品详情（v1.1，含 other_images + specs）。"""
    p = db.get(Product, product_id)
    if not p or p.is_deleted or p.status != "on_sale":
        return None

    other_images: list[str] = []
    if p.other_images_json:
        try:
            if isinstance(p.other_images_json, str):
                other_images = json.loads(p.other_images_json)
            else:
                other_images = p.other_images_json
        except (json.JSONDecodeError, TypeError):
            pass

    def _cat(cid: int | None) -> dict | None:
        if not cid:
            return None
        c = db.get(Category, cid)
        return {"id": c.id, "name": c.name} if c else None

    return ProductDetail(
        id=p.id,
        product_code=p.product_code,
        name=p.name,
        subtitle=p.subtitle,
        cover_url=p.cover_url,
        other_images=other_images,
        description=p.description,
        specs=p.extra_specs,
        min_price_cents=p.min_price_cents,
        max_price_cents=p.max_price_cents,
        is_top=p.is_top,
        status=p.status,
        series=_cat(p.series_id),
        space=_cat(p.space_id),
        category=_cat(p.category_id),
    )


# ===== 后台 CRUD =====

def create_product(db: Session, payload: ProductCreate, admin_id: int) -> Product:
    """创建产品。"""
    p = Product(
        product_code=payload.product_code,
        name=payload.name,
        subtitle=payload.subtitle,
        series_id=payload.series_id,
        space_id=payload.space_id,
        category_id=payload.category_id,
        min_price_cents=payload.min_price_cents,
        max_price_cents=payload.max_price_cents,
        cover_url=payload.cover_url,
        description=payload.description,
        extra_specs=payload.specs,
        other_images_json=payload.other_images,
        support_order=payload.support_order,
        sort=payload.sort,
        status=payload.status,
        is_top=payload.is_top,
        created_at=admin_id,
        updated_at=admin_id,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def update_product(db: Session, product_id: int, payload: ProductCreate, admin_id: int) -> Product | None:
    """更新产品（全字段覆盖式 PUT）。"""
    p = db.get(Product, product_id)
    if not p or p.is_deleted:
        return None
    p.product_code = payload.product_code
    p.name = payload.name
    p.subtitle = payload.subtitle
    p.series_id = payload.series_id
    p.space_id = payload.space_id
    p.category_id = payload.category_id
    p.min_price_cents = payload.min_price_cents
    p.max_price_cents = payload.max_price_cents
    p.cover_url = payload.cover_url
    p.description = payload.description
    p.extra_specs = payload.specs
    p.other_images_json = payload.other_images
    p.support_order = payload.support_order
    p.sort = payload.sort
    p.status = payload.status
    p.is_top = payload.is_top
    p.updated_at = admin_id
    db.commit()
    db.refresh(p)
    return p


def delete_product(db: Session, product_id: int, admin_id: int) -> bool:
    """软删除产品。"""
    p = db.get(Product, product_id)
    if not p or p.is_deleted:
        return False
    from datetime import datetime

    p.is_deleted = 1
    p.deleted_at = datetime.now()
    p.updated_at = admin_id
    db.commit()
    return True


def list_admin_products(
    db: Session,
    *,
    keyword: str | None = None,
    status_filter: str | None = None,
    category_id: int | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    """后台产品列表（含已下架/草稿）。"""
    q = select(Product).where(Product.is_deleted == 0)
    if status_filter:
        q = q.where(Product.status == status_filter)
    if category_id:
        q = q.where(Product.category_id == category_id)
    if keyword:
        q = q.where(Product.name.like(f"%{keyword}%"))

    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    q = q.order_by(Product.is_top.desc(), Product.sort.asc(), Product.id.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(q).all()

    items: list[dict[str, Any]] = []
    for p in rows:
        items.append(
            {
                "id": p.id,
                "product_code": p.product_code,
                "name": p.name,
                "subtitle": p.subtitle,
                "category_id": p.category_id,
                "space_id": p.space_id,
                "series_id": p.series_id,
                "min_price_cents": p.min_price_cents,
                "max_price_cents": p.max_price_cents,
                "cover_url": p.cover_url,
                "status": p.status,
                "is_top": p.is_top,
                "support_order": p.support_order,
                "sort": p.sort,
                "created_date": p.created_date.isoformat() if p.created_date else None,
                "updated_date": p.updated_date.isoformat() if p.updated_date else None,
            }
        )
    return items, total


__all__ = [
    "list_products",
    "get_product_detail",
    "create_product",
    "update_product",
    "delete_product",
    "list_admin_products",
]
