from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), unique=True)
    

    remind_before: Mapped[bool] = mapped_column(Boolean, default=True)
    remind_after: Mapped[bool] = mapped_column(Boolean, default=True)

    remind_start: Mapped[int] = mapped_column(Integer, default=30)

    interval_before_unit: Mapped[str] = mapped_column(String, default="minutes")
    interval_before_deadline: Mapped[int] = mapped_column(Integer, default=10)

    interval_after_unit: Mapped[str] = mapped_column(String, default="minutes")
    interval_after_deadline: Mapped[int] = mapped_column(Integer, default=5)

    remind_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    last_notified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    task: Mapped["Task"] = relationship("Task", back_populates="reminder")