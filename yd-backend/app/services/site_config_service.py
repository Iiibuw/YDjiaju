"""站点配置服务层（后台）。key-value 字典，upsert 语义。"""
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.site_config import SiteConfig
from app.schemas.site_config import SiteConfigIn, SiteConfigOut


def list_site_configs(
    db: Session,
    *,
    category: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[SiteConfigOut], int]:
    q = select(SiteConfig)
    if category:
        q = q.where(SiteConfig.category == category)
    if keyword:
        q = q.where(SiteConfig.config_key.like(f"%{keyword}%"))
    total = db.execute(select(func.count()).select_from(q.subquery())).scalar() or 0
    q = q.order_by(SiteConfig.category, SiteConfig.config_key)
    q = q.offset((page - 1) * page_size).limit(page_size)
    items = [SiteConfigOut.model_validate(r) for r in db.execute(q).scalars().all()]
    return items, total


def get_by_key(db: Session, config_key: str) -> SiteConfig | None:
    return db.scalar(select(SiteConfig).where(SiteConfig.config_key == config_key))


def upsert_site_config(db: Session, payload: SiteConfigIn, admin_id: int) -> SiteConfigOut:
    """按 config_key 更新或新建（站点配置的常见语义）。"""
    cfg = get_by_key(db, payload.config_key)
    data: dict[str, Any] = payload.model_dump()
    if cfg:
        for k, v in data.items():
            setattr(cfg, k, v)
        cfg.updated_at = admin_id
        db.commit()
        db.refresh(cfg)
        return SiteConfigOut.model_validate(cfg)
    data["created_at"] = admin_id
    data["updated_at"] = admin_id
    cfg = SiteConfig(**data)
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return SiteConfigOut.model_validate(cfg)


__all__ = ["list_site_configs", "get_by_key", "upsert_site_config"]
