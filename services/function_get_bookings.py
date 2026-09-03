import logging.config
from datetime import date
from typing import Optional

from core import dict_config
from database import Booking, Person
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logging.config.dictConfig(dict_config)

main_log = logging.getLogger("services_logger")
main_log.setLevel(logging.DEBUG)


async def get_information_about_bookings(
    booking_date: Optional[date], db: AsyncSession
) -> list[tuple[Booking, Person]]:
    """
    Получает список бронирований, при необходимости фильтруя по дате.

    Args:
        booking_date (Optional[date]): Дата бронирования для фильтрации.
            Если None, возвращаются все брони.
        db (AsyncSession): Асинхронная SQLAlchemy-сессия.

    Returns:
        list[tuple[Booking, Person]]: Список кортежей, где каждый элемент
            содержит объект Booking и связанный с ним объект Person.

    Raises:
        HTTPException: 500, если произошла ошибка базы данных.
    """
    main_log.debug(
        "Начало получения списка бронирований. booking_date=%s",
        booking_date,
    )

    try:
        stmt = select(Booking, Person).join(
            Person, Booking.person_id == Person.id
        )

        if booking_date is not None:
            main_log.info(
                "Применяется фильтр по дате бронирования: booking_date=%s",
                booking_date,
            )
            # ← ЯВНО приводим к дате на уровне SQL
            stmt = stmt.where(
                func.date(Booking.booking_date) == booking_date
            )
        else:
            main_log.info("Фильтр по дате не применяется, возвращаем все брони")

        # Отладка: посмотри, какой SQL уходит в БД
        print("SQL:", stmt.compile(compile_kwargs={"literal_binds": True}))

        result = await db.execute(stmt)
        bookings = result.all()

        main_log.info(
            "Список бронирований получен успешно. count=%s",
            len(bookings),
        )
        return bookings

    except SQLAlchemyError as error:
        main_log.exception(
            "Ошибка БД при получении списка бронирований booking_date=%s: %s",
            booking_date,
            error,
        )
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка БД. / Database error.",
        )