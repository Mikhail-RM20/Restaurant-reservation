from enum import Enum as PyEnum

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class BookingStatus(str, PyEnum):
    active = "active"
    cancelled = "cancelled"


class Person(Base):
    __tablename__ = "person"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)

    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
    )


class Booking(Base):
    __tablename__ = "booking_table"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    person_id: Mapped[int] = mapped_column(
        ForeignKey("person.id"), nullable=False
    )
    booking_date: Mapped[Date] = mapped_column(Date, nullable=False)
    booking_time: Mapped[Time] = mapped_column(Time, nullable=False)
    guests: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus),
        nullable=False,
        default=BookingStatus.active,
    )

    person: Mapped["Person"] = relationship(back_populates="bookings")
