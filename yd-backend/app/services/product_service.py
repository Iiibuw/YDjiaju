"""产品服务层。前台公开读 + 后台 CRUD（M1 范围）。"""
import json
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductDetail, ProductListItem


# ===== 公共读（前台） =====

def _cents_to_yuan(min_c: int | None, max_c: int | None) -> str | None:
    """返回纯数字(无 ¥ 符号),由前端 ProductCard 统一加 "¥" 避免双符号。"""
    if min_c is None and max_c is None:
        return None
    if min_c is not None and max_c is None:
        return f"{min_c / 100:.2f}"
    if min_c is None and max_c is not None:
        return f"{max_c / 100:.2f}"
    if min_c == max_c:
        return f"{min_c / 100:.2f}"
    return f"{min_c / 100:.2f} – {max_c / 100:.2f}"


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
    q = q.order_by(Product.is_top.desc(), Product.sort.desc(), Product.id.desc())
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


def get_admin_product(db: Session, product_id: int) -> Product | None:
    """后台获取产品(返回 ORM Product 对象,支持 to_admin_dict 取所有列)。
    与前台 get_product_detail(返回 ProductDetail Pydantic)区别。"""
    p = db.get(Product, product_id)
    if not p or p.is_deleted:
        return None
    return p

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
        style=payload.style,
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


def update_product(db: Session, product_id: int, payload: ProductCreate | ProductUpdate, admin_id: int) -> Product | None:
    """更新产品（部分更新：仅应用客户端显式传入的字段，status-only 上下架不会清空其它字段）。"""
    p = db.get(Product, product_id)
    if not p or p.is_deleted:
        return None
    data = payload.model_dump(exclude_unset=True)
    if "name" in data:
        p.name = data["name"]
    if "subtitle" in data:
        p.subtitle = data["subtitle"]
    if "style" in data:
        p.style = data["style"]
    if "series_id" in data:
        p.series_id = data["series_id"]
    if "space_id" in data:
        p.space_id = data["space_id"]
    if "category_id" in data:
        p.category_id = data["category_id"]
    if "min_price_cents" in data:
        p.min_price_cents = data["min_price_cents"]
    if "max_price_cents" in data:
        p.max_price_cents = data["max_price_cents"]
    if "cover_url" in data:
        p.cover_url = data["cover_url"]
    if "description" in data:
        p.description = data["description"]
    if "specs" in data:
        p.extra_specs = data["specs"]
    if "other_images" in data:
        p.other_images_json = data["other_images"]
    if "support_order" in data:
        p.support_order = data["support_order"]
    if "sort" in data:
        p.sort = data["sort"]
    if "status" in data:
        p.status = data["status"]
    if "is_top" in data:
        p.is_top = data["is_top"]
    if "product_code" in data:
        p.product_code = data["product_code"]
    # 约束:最低价 ≤ 最高价
    if p.min_price_cents is not None and p.max_price_cents is not None and p.min_price_cents > p.max_price_cents:
        db.rollback()
        raise ValueError("最低价不能大于最高价")
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
    q = q.order_by(Product.is_top.desc(), Product.sort.desc(), Product.id.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(q).all()

    # 一次性查询分类名,补 space_name / series_name / category_name
    cat_ids: set[int] = set()
    for row in rows:
        cat_ids.update({row.space_id, row.series_id, row.category_id})
    cat_ids.discard(None)
    cat_names: dict[int, str] = {}
    if cat_ids:
        for c in db.scalars(select(Category).where(Category.id.in_(cat_ids))).all():
            cat_names[c.id] = c.name

    items: list[dict[str, Any]] = []
    for p in rows:
        d = to_admin_dict(p)
        d["space_name"] = cat_names.get(p.space_id)
        d["series_name"] = cat_names.get(p.series_id)
        d["category_name"] = cat_names.get(p.category_id)
        items.append(d)
    return items, total


__all__ = [
    "list_products",
    "get_product_detail",
    "create_product",
    "update_product",
    "delete_product",
    "get_admin_product",
    "list_admin_products",
    "to_admin_dict",
]


def to_admin_dict(p: Product) -> dict[str, Any]:
    """把 Product ORM 对象转为可 JSON 序列化的 dict（剔除 SQLAlchemy 内部状态）。

    用于后台 CRUD 接口的响应。
    """
    return {
        "id": p.id,
        "product_code": p.product_code,
        "name": p.name,
        "subtitle": p.subtitle,
        "style": p.style,
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
        "description": p.description,
        "extra_specs": p.extra_specs,
        "other_images": p.other_images_json,
        "is_activate": p.is_activate,
        "is_deleted": p.is_deleted,
        "created_date": p.created_date.isoformat() if p.created_date else None,
        "updated_date": p.updated_date.isoformat() if p.updated_date else None,
    }
