from datetime import date, timedelta, time

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, get_db
from database import Person, Booking, BookingStatus
from schemas import BookingCreateIn, BookingCreateOut


class TestDatabase:
    """Проверяем, что ORO-модели корректно работают с БД."""

    @pytest.mark.asyncio
    async def test_create_person_and_booking(self, db_session: AsyncSession):
        """Позитив: создание Person и связанной Booking."""
        person = Person(name="Анна", phone="88005553535")
        db_session.add(person)
        await db_session.flush()

        booking = Booking(
            person_id=person.id,
            booking_date=date.today() + timedelta(days=1),
            booking_time=time(18, 0),
            guests=2,
            status=BookingStatus.active,
        )
        db_session.add(booking)
        await db_session.commit()

        assert person.id is not None
        assert booking.id is not None
        assert booking.person_id == person.id
        assert booking.status == BookingStatus.active

    @pytest.mark.asyncio
    async def test_cascade_delete_person(self, db_session: AsyncSession):
        """Позитив: удаление Person каскадно удаляет брони."""
        person = Person(name="Каскад", phone="88000000000")
        db_session.add(person)
        await db_session.flush()

        booking = Booking(
            person_id=person.id,
            booking_date=date.today(),
            booking_time=time(12, 0),
            guests=1,
            status=BookingStatus.cancelled,
        )
        db_session.add(booking)
        await db_session.commit()

        await db_session.delete(person)
        await db_session.commit()

        # После каскадного удаления бронь должна исчезнуть
        from sqlalchemy import select
        result = await db_session.execute(select(Booking).where(Booking.id == booking.id))
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_booking_status_enum_values(self, db_session: AsyncSession):
        person = Person(name="Enum", phone="81111111111")
        db_session.add(person)
        await db_session.flush()

        for st in (BookingStatus.active, BookingStatus.cancelled):
            b = Booking(
                person_id=person.id,
                booking_date=date.today(),
                booking_time=time(12, 0),
                guests=1,
                status=st,
            )
            db_session.add(b)

        await db_session.commit()

        from sqlalchemy import select, func
        result = await db_session.execute(select(func.count(Booking.id)))
        count = result.scalar_one()
        assert count >= 2

    @pytest.mark.asyncio
    async def test_booking_without_person_fails(self, db_session: AsyncSession):
        """Негатив: бронь без person_id нарушает NOT NULL (ожидается IntegrityError)."""
        booking = Booking(
            person_id=None,  # нарушение nullable=False
            booking_date=date.today(),
            booking_time=time(12, 0),
            guests=1,
            status=BookingStatus.active,
        )
        db_session.add(booking)
        with pytest.raises(Exception):  # IntegrityError или аналог
            await db_session.commit()
        await db_session.rollback()
