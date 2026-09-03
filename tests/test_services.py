from datetime import date, timedelta, time

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database import BookingStatus, Person, Booking
from shemas import BookingCreateIn
from services import add_new_booking, get_information_about_bookings, get_booking_by_id, delete_booking


class TestServices:
    """Unit-тесты бизнес-логики без HTTP-слоя."""

    # ======================= add_new_booking =======================

    @pytest.mark.asyncio
    async def test_add_new_booking_success(self, db_session: AsyncSession, sample_booking_in):
        """Позитив: успешное создание брони."""
        booking, person = await add_new_booking(sample_booking_in, db_session)
        assert booking.id is not None
        assert person.name == sample_booking_in.name
        assert booking.status == BookingStatus.active

    @pytest.mark.asyncio
    async def test_add_new_booking_duplicate_time(self, db_session: AsyncSession, sample_booking_in):
        """Негатив: попытка создать бронь на то же время → 409 Conflict."""
        await add_new_booking(sample_booking_in, db_session)
        # тот же объект нельзя повторно использовать с той же сессией,
        # поэтому создаём копию
        duplicate = BookingCreateIn(
            name="Другой Человек",
            phone="+79161234568",
            booking_date=sample_booking_in.booking_date,
            booking_time=sample_booking_in.booking_time,
            guests=2,
        )
        with pytest.raises(Exception) as exc_info:
            await add_new_booking(duplicate, db_session)
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_add_new_booking_rollback_on_error(self, db_session: AsyncSession, sample_booking_in):
        """Негатив: при конфликте в БД не остаётся «грязных» записей."""
        await add_new_booking(sample_booking_in, db_session)
        duplicate = BookingCreateIn(
            name="Ошибка",
            phone="+79161234569",
            booking_date=sample_booking_in.booking_date,
            booking_time=sample_booking_in.booking_time,
            guests=1,
        )
        try:
            await add_new_booking(duplicate, db_session)
        except Exception:
            pass

        from sqlalchemy import select
        result = await db_session.execute(select(Person).where(Person.name == "Ошибка"))
        assert result.scalar_one_or_none() is None

    # ======================= get_information_about_bookings =======================

    @pytest.mark.asyncio
    async def test_get_bookings_empty(self, db_session: AsyncSession):
        """Позитив: пустая таблица → пустой список."""
        result = await get_information_about_bookings(None, db_session)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_bookings_filter_by_date(self, db_session: AsyncSession):
        """Позитив: фильтрация по дате возвращает только нужные записи."""
        person = Person(name="Фильтр", phone="82222222222")
        db_session.add(person)
        await db_session.flush()

        d1 = date.today() + timedelta(days=2)
        d2 = date.today() + timedelta(days=3)

        b1 = Booking(person_id=person.id, booking_date=d1, booking_time=time(12, 0), guests=1, status=BookingStatus.active)
        b2 = Booking(person_id=person.id, booking_date=d2, booking_time=time(13, 0), guests=2, status=BookingStatus.active)
        db_session.add_all([b1, b2])
        await db_session.commit()

        result = await get_information_about_bookings(d1, db_session)
        assert len(result) == 1
        assert result[0][0].booking_date == d1

    @pytest.mark.asyncio
    async def test_get_bookings_all(self, db_session: AsyncSession):
        """Позитив: без фильтра возвращаются все брони."""
        person = Person(name="Все", phone="83333333333")
        db_session.add(person)
        await db_session.flush()

        for h in (14, 15):
            db_session.add(Booking(
                person_id=person.id,
                booking_date=date.today() + timedelta(days=1),
                booking_time=time(h, 0),
                guests=1,
                status=BookingStatus.active,
            ))
        await db_session.commit()

        result = await get_information_about_bookings(None, db_session)
        assert len(result) == 2

    # ======================= get_booking_by_id =======================

    @pytest.mark.asyncio
    async def test_get_booking_by_id_success(self, db_session: AsyncSession):
        """Позитив: получение существующей брони."""
        person = Person(name="Поиск", phone="84444444444")
        db_session.add(person)
        await db_session.flush()

        booking = Booking(
            person_id=person.id,
            booking_date=date.today(),
            booking_time=time(18, 0),
            guests=3,
            status=BookingStatus.active,
        )
        db_session.add(booking)
        await db_session.commit()

        b, p = await get_booking_by_id(booking.id, db_session)
        assert b.id == booking.id
        assert p.name == "Поиск"

    @pytest.mark.asyncio
    async def test_get_booking_by_id_not_found(self, db_session: AsyncSession):
        """Негатив: запрос несуществующего ID → 404."""
        with pytest.raises(Exception) as exc_info:
            await get_booking_by_id(999999, db_session)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_booking_by_id_invalid_id_type(self, db_session: AsyncSession):
        """Негатив: логическая проверка — отрицательный ID не найден."""
        with pytest.raises(Exception) as exc_info:
            await get_booking_by_id(-1, db_session)
        assert exc_info.value.status_code == 404

    # ======================= delete_booking =======================

    @pytest.mark.asyncio
    async def test_delete_booking_already_cancelled(self, db_session: AsyncSession):
        person = Person(name="Удаление", phone="85555555555")
        db_session.add(person)
        await db_session.flush()

        booking = Booking(
            person_id=person.id,
            booking_date=date.today(),
            booking_time=time(19, 0),
            guests=5,
            status=BookingStatus.cancelled,
        )
        db_session.add(booking)
        await db_session.commit()

        with pytest.raises(Exception) as exc_info:
            await delete_booking(booking.id, db_session)

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_delete_booking_not_found(self, db_session: AsyncSession):
        """Негатив: отмена несуществующей брони → 404."""
        with pytest.raises(Exception) as exc_info:
            await delete_booking(999999, db_session)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_booking_idempotent_status(self, db_session: AsyncSession):
        person = Person(name="Повтор", phone="86666666666")
        db_session.add(person)
        await db_session.flush()

        booking = Booking(
            person_id=person.id,
            booking_date=date.today(),
            booking_time=time(20, 0),
            guests=1,
            status=BookingStatus.cancelled,
        )
        db_session.add(booking)
        await db_session.commit()

        with pytest.raises(Exception) as exc_info:
            await delete_booking(booking.id, db_session)

        assert exc_info.value.status_code == 409
