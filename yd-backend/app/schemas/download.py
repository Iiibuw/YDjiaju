"""下载中心 Pydantic 模型（对齐数据库设计文档 §4.3.7）。"""
from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class DownloadIn(BaseModel):
    """后台创建/更新下载资料。"""

    title: str = Field(min_length=1, max_length=128, description="资料标题")
    category: str = Field(default="catalog", pattern="^(catalog|manual|cad|other)$", description="资料分类")
    description: str | None = Field(default=None, max_length=500, description="简介")
    file_url: str = Field(min_length=1, max_length=255, description="文件 URL")
    file_size_kb: int | None = Field(default=None, ge=0, description="文件大小（KB）")
    file_format: str | None = Field(default=None, max_length=16, description="文件格式（pdf/zip/docx...）")
    sort: int = Field(default=0, description="排序")
    is_activate: int = Field(default=1, ge=0, le=1, description="1激活 0禁用")


class DownloadOut(ORMBase):
    """后台下载列表项/详情。"""

    id: int
    title: str
    category: str
    description: str | None = None
    file_url: str
    file_size_kb: int | None = None
    file_format: str | None = None
    download_count: int = 0
    sort: int = 0
    is_activate: int = 1
