
from datetime import datetime, date, time

from sqlalchemy import (
    String,
    Date,
    Time,
    DateTime,
    Integer,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class InterviewBooking(Base):
    __tablename__ = "interview_bookings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    session_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    interview_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    interview_time: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
