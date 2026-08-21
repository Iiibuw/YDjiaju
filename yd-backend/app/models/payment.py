"""支付记录（二期接口占位）。

字段以数据库设计文档 §4.6.3 为准。
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, Integer, JSON, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class Payment(Base, AuditMixin):
    __tablename__ = "payments"
    __table_args__ = (
        Index("IDX_payments_order_id", "order_id"),
        Index("IDX_payments_status", "status"),
        Index("IDX_payments_is_activate", "is_activate"),
        Index("IDX_payments_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "支付记录",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("orders.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="所属订单",
    )
    channel: Mapped[str] = mapped_column(
        Enum("wechat", "alipay", "offline", name="enum_payment_channel"),
        nullable=False,
        default="wechat",
        server_default="wechat",
        comment="支付渠道（二期）",
    )
    transaction_id: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="第三方交易号")
    amount_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="支付金额（分）")
    status: Mapped[str] = mapped_column(
        Enum("pending", "success", "failed", "refunded", name="enum_payment_status"),
        nullable=False,
        default="pending",
        server_default="pending",
        comment="支付状态",
    )
    paid_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True, comment="支付完成时间")
    raw_response: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="第三方返回原始数据")
