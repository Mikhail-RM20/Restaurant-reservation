import logging.config

from core import dict_config
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from services import delete_booking
from schemas import BookingCreateOut
from sqlalchemy.ext.asyncio import AsyncSession

logging.config.dictConfig(dict_config)

main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)

router = APIRouter()


@router.delete("/bookings/{id}", response_model=BookingCreateOut)
async def delete_booking_by_id(id: int, db: AsyncSession = Depends(get_db)):
    """
    Отменяет бронирование по его ID.

    Args:
        id (int): ID брони, которую нужно отменить.
        db (AsyncSession): Асинхронная SQLAlchemy-сессия, получаемая через Depends(get_db).

    Returns:
        BookingCreateOut: Данные отменённой брони, включая:
            - id: ID брони
            - name: имя человека
            - booking_date: дата бронирования
            - booking_time: время бронирования
            - guests: количество гостей
            - status: текущий статус брони

    Raises:
        HTTPException: 500, если произошла непредвиденная ошибка сервера.
    """
    main_log.debug("Начало обработки DELETE /bookings/%s", id)
    try:
        main_log.info("Запрос на поиск брони по id=%s", id)
        booking, person = await delete_booking(booking_id=id, db=db)
        main_log.info(
            "Бронь найдена: booking_id=%s, person_id=%s, name=%s",
            booking.id,
            booking.person_id,
            person.name,
        )

        return BookingCreateOut(
            id=booking.id,
            name=person.name,
            phone=person.phone,
            booking_date=booking.booking_date,
            booking_time=booking.booking_time,
            guests=booking.guests,
            status=booking.status,
        )

    except HTTPException as e:
        main_log.exception("Ошибка при обработке POST /bookings: %s", e)
        raise
