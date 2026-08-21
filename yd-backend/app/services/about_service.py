"""关于我们服务层（后台）。区块 + 图集（about_images，全量替换语义）。"""
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.about_image import AboutImage
from app.models.about_section import AboutSection
from app.schemas.about import AboutImageOut, AboutSectionIn, AboutSectionOut


def _attach_images(db: Session, out: AboutSectionOut) -> AboutSectionOut:
    imgs = db.execute(
        select(AboutImage)
        .where(AboutImage.section_id == out.id, AboutImage.is_deleted == 0)
        .order_by(AboutImage.sort, AboutImage.id)
    ).scalars().all()
    out.images = [AboutImageOut.model_validate(i) for i in imgs]
    return out


def list_about_sections(db: Session) -> list[AboutSectionOut]:
    rows = db.execute(
        select(AboutSection).where(AboutSection.is_deleted == 0).order_by(AboutSection.sort, AboutSection.id)
    ).scalars().all()
    return [_attach_images(db, AboutSectionOut.model_validate(r)) for r in rows]


def get_about_section(db: Session, section_id: int) -> AboutSectionOut | None:
    s = db.get(AboutSection, section_id)
    if not s or s.is_deleted:
        return None
    return _attach_images(db, AboutSectionOut.model_validate(s))


def create_about_section(db: Session, payload: AboutSectionIn, admin_id: int) -> AboutSectionOut:
    data: dict[str, Any] = payload.model_dump(exclude={"images"})
    data["created_at"] = admin_id
    data["updated_at"] = admin_id
    s = AboutSection(**data)
    db.add(s)
    db.flush()
    _replace_images(db, s.id, payload.images, admin_id)
    db.commit()
    db.refresh(s)
    return _attach_images(db, AboutSectionOut.model_validate(s))


def update_about_section(db: Session, section_id: int, payload: AboutSectionIn, admin_id: int) -> AboutSectionOut | None:
    s = db.get(AboutSection, section_id)
    if not s or s.is_deleted:
        return None
    for k, v in payload.model_dump(exclude={"images"}).items():
        setattr(s, k, v)
    s.updated_at = admin_id
    _replace_images(db, s.id, payload.images, admin_id)
    db.commit()
    db.refresh(s)
    return _attach_images(db, AboutSectionOut.model_validate(s))


def _replace_images(db: Session, section_id: int, images: list, admin_id: int) -> None:
    """图集全量替换：旧图软删，新图插入。"""
    old = db.execute(select(AboutImage).where(AboutImage.section_id == section_id, AboutImage.is_deleted == 0)).scalars().all()
    for o in old:
        o.is_deleted = 1
        o.updated_at = admin_id
    for i, img in enumerate(images):
        db.add(
            AboutImage(
                section_id=section_id,
                url=img.url,
                caption=img.caption,
                sort=img.sort if img.sort is not None else i,
                created_at=admin_id,
                updated_at=admin_id,
            )
        )


def delete_about_section(db: Session, section_id: int, admin_id: int) -> bool:
    """软删除区块，并级联软删其图集。"""
    s = db.get(AboutSection, section_id)
    if not s or s.is_deleted:
        return False
    s.is_deleted = 1
    s.updated_at = admin_id
    for o in db.execute(select(AboutImage).where(AboutImage.section_id == section_id, AboutImage.is_deleted == 0)).scalars().all():
        o.is_deleted = 1
        o.updated_at = admin_id
    db.commit()
    return True


__all__ = ["list_about_sections", "get_about_section", "create_about_section", "update_about_section", "delete_about_section"]
