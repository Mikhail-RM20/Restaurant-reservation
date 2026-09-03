import logging.config

from core import dict_config
from database import Booking, BookingStatus, Person
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logging.config.dictConfig(dict_config)

main_log = logging.getLogger("services_logger")
main_log.setLevel(logging.DEBUG)


async def delete_booking(
    booking_id: int, db: AsyncSession
) -> tuple[Booking, Person]:
    """
    Отменяет бронирование по ID без физического удаления записи.

    Args:
        booking_id (int): ID брони, которую нужно отменить.
        db (AsyncSession): Асинхронная SQLAlchemy-сессия.

    Returns:
        tuple[Booking, Person]: Кортеж из брони и связанного человека.

    Raises:
        HTTPException: 404, если бронь не найдена.
        HTTPException: 500, если произошла ошибка базы данных.
    """
    main_log.debug("Начало отмены брони id=%s", booking_id)

    try:
        stmt = (
            select(Booking, Person)
            .join(Person, Booking.person_id == Person.id)
            .where(Booking.id == booking_id)
        )

        main_log.info("Поиск брони для отмены id=%s", booking_id)

        result = await db.execute(stmt)
        row = result.first()

        if row is None:
            main_log.info(
                "Бронь для отмены не найдена: booking_id=%s", booking_id
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Бронь не найдена. / Booking not found.",
            )

        booking, person = row

        booking.status = BookingStatus.cancelled
        main_log.info(
            "Статус брони изменён на cancelled: booking_id=%s, person_id=%s, name=%s",
            booking.id,
            booking.person_id,
            person.name,
        )

        await db.commit()
        main_log.debug("Коммит выполнен для booking_id=%s", booking_id)

        await db.refresh(booking)
        main_log.debug("Booking обновлён из БД: booking_id=%s", booking.id)

        return booking, person

    except SQLAlchemyError as e:
        main_log.exception(
            "Ошибка БД при отмене брони id=%s: %s", booking_id, e
        )
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка БД. / Database error.",
        )
