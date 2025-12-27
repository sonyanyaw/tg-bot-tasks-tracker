from datetime import date, datetime
from sqlalchemy import BigInteger, Date, DateTime, String
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

from app.db.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)

    # timezone: Mapped[str] = mapped_column()
    # created_at: Mapped[date] = mapped_column(Date, default=date.today)

    timezone: Mapped[str] = mapped_column(default="Europe/Moscow")
    language: Mapped[str] = mapped_column(String(10), default="ru")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )


    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="user", cascade="all, delete-orphan")