"""通用文件上传端点（图片优先，其他文件兜底）。
- POST /api/v1/upload/image：限制 png/jpg/jpeg/webp/gif，5MB 以内
- POST /api/v1/upload/file：通用文件，10MB 以内
- 文件保存到 backend/static/uploads/，通过 /static/uploads/* 公网访问
- 生产环境建议把 static/ 挂到对象存储（OSS/S3），本地保存仅供开发
"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app.core.config import settings
from app.schemas.common import ApiResponse

router = APIRouter()

# 保存目录：相对 backend/ 工作目录的 static/uploads
# 路径计算：__file__ = yd-backend/app/api/v1/endpoints/upload.py
#           5 个 .parent = yd-backend/  → 与 main.py mount 的 static/ 一致
_STATIC_DIR = Path(__file__).resolve().parents[4] / "static" / "uploads"
_STATIC_DIR.mkdir(parents=True, exist_ok=True)

# 图片上传白名单
_IMAGE_EXTS = {"png", "jpg", "jpeg", "webp", "gif"}
_IMAGE_MAX_BYTES = 5 * 1024 * 1024  # 5MB

# 通用文件兜底
_FILE_EXTS = {"pdf", "doc", "docx", "xls", "xlsx", "txt", "zip"}
_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB


def _save_file(file: UploadFile, allowed_exts: set[str], max_bytes: int, subdir: str) -> tuple[Path, str, int]:
    """保存上传文件，返回 (路径, 公网文件名, 大小)。"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供文件名")

    # 取扩展名（小写、不带点）
    raw_ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if raw_ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型 .{raw_ext},允许: {', '.join(sorted(allowed_exts))}",
        )

    # 读取并校验大小（这里一次性读，5MB 不会爆内存）
    content = file.file.read()
    size = len(content)
    if size > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"文件过大 ({size // 1024} KB),上限 {max_bytes // (1024 * 1024)} MB",
        )
    if size == 0:
        raise HTTPException(status_code=400, detail="文件为空")

    # 命名：{subdir}/{uuid}.{ext}
    new_filename = f"{uuid.uuid4().hex}.{raw_ext}"
    target_dir = _STATIC_DIR / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / new_filename
    target_path.write_bytes(content)

    return target_path, new_filename, size


@router.post("/upload/image", response_model=ApiResponse[dict])
async def upload_image(request: Request, file: UploadFile = File(...)):
    """上传图片：支持 png/jpg/jpeg/webp/gif，≤5MB。

    响应 data: { url, filename, size, content_type }
    """
    _, filename, size = _save_file(file, _IMAGE_EXTS, _IMAGE_MAX_BYTES, "images")
    public_url = f"{request.base_url}static/uploads/images/{filename}"
    return ApiResponse(
        data={
            "url": public_url,
            "filename": filename,
            "size": size,
            "content_type": file.content_type or "image/*",
        },
        message="上传成功",
    )


@router.post("/upload/file", response_model=ApiResponse[dict])
async def upload_file(request: Request, file: UploadFile = File(...)):
    """上传通用文件（PDF / Word / Excel / ZIP），≤10MB。"""
    _, filename, size = _save_file(file, _FILE_EXTS, _FILE_MAX_BYTES, "files")
    public_url = f"{request.base_url}static/uploads/files/{filename}"
    return ApiResponse(
        data={
            "url": public_url,
            "filename": filename,
            "size": size,
            "content_type": file.content_type or "application/octet-stream",
        },
        message="上传成功",
    )