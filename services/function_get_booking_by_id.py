import logging.config

from core import dict_config
from database import Booking, Person
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logging.config.dictConfig(dict_config)

main_log = logging.getLogger("services_logger")
main_log.setLevel(logging.DEBUG)


async def get_booking_by_id(
    booking_id: int, db: AsyncSession
) -> tuple[Booking, Person]:
    """
    Получает бронь и связанного с ней человека по ID брони.

    Args:
        booking_id (int): ID брони, которую нужно найти.
        db (AsyncSession): Асинхронная SQLAlchemy-сессия.

    Returns:
        tuple[Booking, Person]: Кортеж из объекта Booking и объекта Person.

    Raises:
        HTTPException: 404, если бронь не найдена.
        HTTPException: 500, если произошла ошибка базы данных.
    """
    main_log.debug("Начало поиска брони по id=%s", booking_id)

    try:
        stmt = (
            select(Booking, Person)
            .join(Person, Booking.person_id == Person.id)
            .where(Booking.id == booking_id)
        )
        main_log.info(
            "Выполняется запрос на получение брони id=%s", booking_id
        )
        result = await db.execute(stmt)
        row = result.first()

        if row is None:
            main_log.info("Бронь не найдена: booking_id=%s", booking_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Бронь не найдена. / Booking not found.",
            )

        booking, person = row
        main_log.info(
            "Бронь найдена: booking_id=%s, person_id=%s, name=%s",
            booking.id,
            booking.person_id,
            person.name,
        )
        return booking, person

    except SQLAlchemyError :
        main_log.exception(
            "Ошибка БД при поиске брони id=%s: %s", booking_id,
        )
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка БД. / Database error.",
        )
