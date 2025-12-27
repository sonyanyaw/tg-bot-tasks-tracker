from datetime import date
from sqlalchemy import (
    Date,
    ForeignKey,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.utils.enums import TaskStatusEnum


class TaskStatus(Base):
    __tablename__ = "task_statuses"

    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "task_date",
            name="uq_task_status_task_date"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), index=True)

    task_date: Mapped[date] = mapped_column(Date, index=True)

    status: Mapped[TaskStatusEnum] = mapped_column(Enum(TaskStatusEnum), default=TaskStatusEnum.pending)

    task: Mapped["Task"] = relationship(back_populates="statuses")
