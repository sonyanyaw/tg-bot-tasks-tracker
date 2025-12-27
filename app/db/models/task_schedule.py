from datetime import time
from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String, Integer, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.db.models.base import Base


# class TaskSchedule(Base):
#     __tablename__ = "task_schedules"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))

#     weekday: Mapped[int] = mapped_column(Integer)  
#     # 0=Mon ... 6=Sun

#     time: Mapped[time] = mapped_column(Time)


class TaskSchedule(Base):
    __tablename__ = "task_schedules"

    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "weekday",
            "task_time",
            name="uq_task_weekday_time"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), index=True)

    weekday: Mapped[int] = mapped_column(Integer)
    task_time: Mapped[time] = mapped_column(Time)

    task: Mapped["Task"] = relationship("Task", back_populates="schedules")

    @validates("weekday")
    def validate_weekday(self, key, value):
        if not 0 <= value <= 6:
            raise ValueError("weekday must be between 0 and 6")
        return value
