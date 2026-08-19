"""仓储层入口。当前仅暴露数据范围过滤工具（ADR-004）。"""
from .base import (
    DATA_SCOPED_MODELS,
    DataScope,
    apply_data_scope,
    ensure_data_scope,
    is_data_scoped,
)

__all__ = [
    "DATA_SCOPED_MODELS",
    "DataScope",
    "apply_data_scope",
    "ensure_data_scope",
    "is_data_scoped",
]
