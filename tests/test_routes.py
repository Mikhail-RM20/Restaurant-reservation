from datetime import date, timedelta, time

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from database import BookingStatus, Person, Booking


class TestRoutes:
    # ======================= POST /bookings =======================

    @pytest.mark.asyncio
    async def test_route_create_booking_success(self, client: AsyncClient, sample_booking_in):
        payload = sample_booking_in.model_dump(mode="json")
        response = await client.post("/bookings", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == sample_booking_in.name
        assert data["status"] == BookingStatus.confirmed.value

    @pytest.mark.asyncio
    async def test_route_create_booking_duplicate(self, client: AsyncClient, sample_booking_in):
        payload = sample_booking_in.model_dump(mode="json")
        r1 = await client.post("/bookings", json=payload)
        assert r1.status_code == 201

        payload2 = sample_booking_in.model_dump(mode="json")
        payload2["name"] = "Другой"
        payload2["phone"] = "+79161234568"

        r2 = await client.post("/bookings", json=payload2)
        assert r2.status_code == 409
        assert "уже есть бронь" in r2.text

    @pytest.mark.asyncio
    async def test_route_create_booking_invalid_phone(self, client: AsyncClient):
        payload = {
            "name": "Тест",
            "phone": "not-a-phone",
            "booking_date": (date.today() + timedelta(days=1)).isoformat(),
            "booking_time": "19:00:00",
            "guests": 2,
        }
        response = await client.post("/bookings", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_route_create_booking_past_date(self, client: AsyncClient):
        payload = {
            "name": "Тест",
            "phone": "+79161234567",
            "booking_date": (date.today() - timedelta(days=1)).isoformat(),
            "booking_time": "19:00:00",
            "guests": 2,
        }
        response = await client.post("/bookings", json=payload)
        assert response.status_code == 422

    # ======================= GET /bookings =======================

    @pytest.mark.asyncio
    async def test_route_get_booking_by_id_not_found(self, client: AsyncClient):
        response = await client.get("/bookings/999999")
        assert response.status_code == 404
        assert response.json() == {
            "detail": "Бронь не найдена. / Booking not found."
        }

    @pytest.mark.asyncio
    async def test_route_get_bookings_with_filter(self, client: AsyncClient, db_session: AsyncSession):
        target_date = date.today() + timedelta(days=7)
        person = Person(name="РоутФильтр", phone="87777777777")
        db_session.add(person)
        await db_session.flush()

        db_session.add(Booking(
            person_id=person.id,
            booking_date=target_date,
            booking_time=time(18, 0),
            guests=2,
            status=BookingStatus.confirmed,
        ))
        await db_session.commit()

        response = await client.get(f"/bookings?date={target_date.isoformat()}")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["booking_date"] == target_date.isoformat()

    @pytest.mark.asyncio
    async def test_route_get_bookings_all(self, client: AsyncClient, db_session: AsyncSession):
        person = Person(name="РоутВсе", phone="88888888888")
        db_session.add(person)
        await db_session.flush()

        for h in (12, 13):
            db_session.add(Booking(
                person_id=person.id,
                booking_date=date.today() + timedelta(days=2),
                booking_time=time(h, 0),
                guests=1,
                status=BookingStatus.pending,
            ))
        await db_session.commit()

        response = await client.get("/bookings")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_route_get_bookings_invalid_date_format(self, client: AsyncClient):
        response = await client.get("/bookings?date=not-a-date")
        assert response.status_code == 422

    # ======================= GET /bookings/{id} =======================

    @pytest.mark.asyncio
    async def test_route_get_booking_by_id_success(self, client: AsyncClient, db_session: AsyncSession):
        person = Person(name="РоутПоID", phone="89999999999")
        db_session.add(person)
        await db_session.flush()

        booking = Booking(
            person_id=person.id,
            booking_date=date.today(),
            booking_time=time(20, 0),
            guests=4,
            status=BookingStatus.confirmed,
        )
        db_session.add(booking)
        await db_session.commit()
        await db_session.refresh(booking)

        response = await client.get(f"/bookings/{booking.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == booking.id
        assert data["name"] == "РоутПоID"

    @pytest.mark.asyncio
    async def test_route_get_booking_by_id_not_found(self, client: AsyncClient):
        response = await client.get("/bookings/999999")
        assert response.status_code == 404
        assert "Бронь не найдена" in response.text or "Booking not found" in response.text

    @pytest.mark.asyncio
    async def test_route_get_booking_by_id_invalid_type(self, client: AsyncClient):
        response = await client.get("/bookings/abc")
        assert response.status_code == 422

    # ======================= DELETE /bookings/{id} =======================

    @pytest.mark.asyncio
    async def test_route_delete_booking_success(self, client: AsyncClient, db_session: AsyncSession):
        person = Person(name="РоутУдаление", phone="81111111111")
        db_session.add(person)
        await db_session.flush()

        booking = Booking(
            person_id=person.id,
            booking_date=date.today(),
            booking_time=time(21, 0),
            guests=6,
            status=BookingStatus.confirmed,
        )
        db_session.add(booking)
        await db_session.commit()
        await db_session.refresh(booking)

        response = await client.delete(f"/bookings/{booking.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == BookingStatus.cancelled.value

    @pytest.mark.asyncio
    async def test_route_delete_booking_not_found(self, client: AsyncClient):
        response = await client.delete("/bookings/999999")
        assert response.status_code == 404
        assert "Бронь не найдена" in response.text or "Booking not found" in response.text

    @pytest.mark.asyncio
    async def test_route_delete_booking_invalid_id(self, client: AsyncClient):
        response = await client.delete("/bookings/xyz")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_route_delete_booking_twice(self, client: AsyncClient, db_session: AsyncSession):
        person = Person(name="РоутДвойное", phone="82222222222")
        db_session.add(person)
        await db_session.flush()

        booking = Booking(
            person_id=person.id,
            booking_date=date.today(),
            booking_time=time(22, 0),
            guests=1,
            status=BookingStatus.cancelled,
        )
        db_session.add(booking)
        await db_session.commit()
        await db_session.refresh(booking)

        response = await client.delete(f"/bookings/{booking.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == BookingStatus.cancelled.value