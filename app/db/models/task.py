from datetime import date, datetime, timezone
from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.utils.enums import TaskRepeatRule


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    

    # created_at: Mapped[date] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    repeat_rule: Mapped[TaskRepeatRule] = mapped_column(Enum(TaskRepeatRule), default=TaskRepeatRule.none)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # recurrence: Mapped[str] = mapped_column(String)
    # next_occurrence: Mapped[str] = mapped_column(String, nullable=True)


    user: Mapped["User"] = relationship("User", back_populates="tasks")

    reminder: Mapped["Reminder"] = relationship("Reminder", back_populates="task", uselist=False, cascade="all, delete-orphan")

    schedules: Mapped[list["TaskSchedule"]] = relationship("TaskSchedule", back_populates="task", cascade="all, delete-orphan")

    statuses: Mapped[list["TaskStatus"]] = relationship(back_populates="task", cascade="all, delete-orphan")

    reminder_messages: Mapped[list["ReminderMessage"]] = relationship("ReminderMessage", back_populates="task", cascade="all, delete-orphan")

    
