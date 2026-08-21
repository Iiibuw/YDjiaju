"""前台关于我们 API（公开）：启用中的区块 + 图集。"""
from fastapi import APIRouter
from sqlalchemy import select

from app.core.deps import DbDep
from app.models.about_image import AboutImage
from app.models.about_section import AboutSection
from app.schemas.about import AboutImageOut, AboutSectionOut
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/public/about-sections", tags=["前台-关于我们"])


@router.get("", response_model=ApiResponse[list[AboutSectionOut]])
def list_about_sections(db: DbDep):
    """启用中的关于区块（含图集），按 sort 排序。"""
    rows = db.execute(
        select(AboutSection)
        .where(AboutSection.is_deleted == 0, AboutSection.is_activate == 1)
        .order_by(AboutSection.sort, AboutSection.id)
    ).scalars().all()

    items: list[AboutSectionOut] = []
    for r in rows:
        out = AboutSectionOut.model_validate(r)
        imgs = db.execute(
            select(AboutImage)
            .where(AboutImage.section_id == r.id, AboutImage.is_deleted == 0)
            .order_by(AboutImage.sort, AboutImage.id)
        ).scalars().all()
        out.images = [AboutImageOut.model_validate(i) for i in imgs]
        items.append(out)
    return ApiResponse(data=items)
