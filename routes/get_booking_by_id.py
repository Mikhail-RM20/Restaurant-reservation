import logging.config

from core import dict_config
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from schemas import BookingCreateOut
from services import get_booking_by_id
from sqlalchemy.ext.asyncio import AsyncSession

logging.config.dictConfig(dict_config)

main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)


router = APIRouter()


@router.get(
    "/bookings/{id}",
    response_model=BookingCreateOut,
    status_code=status.HTTP_200_OK,
)
async def get_booking_table_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Возвращает данные брони по её ID.

    Args:
        id (int): ID брони, которую нужно получить.
        db (AsyncSession): Асинхронная SQLAlchemy-сессия, получаемая через Depends(get_db).

    Returns:
        BookingCreateOut: Данные брони, включая:
            - id: ID брони
            - name: имя человека, к которому привязана бронь
            - booking_date: дата бронирования
            - booking_time: время бронирования
            - guests: количество гостей
            - status: текущий статус брони

    Raises:
        HTTPException: 500, если произошла непредвиденная ошибка сервера.
    """
    main_log.debug("Начало обработки GET /bookings/%s", id)
    try:
        main_log.info("Запрос на получение брони по id=%s", id)
        booking, person = await get_booking_by_id(booking_id=id, db=db)
        main_log.info(
            "Бронь успешно найдена: booking_id=%s, person_id=%s, name=%s",
            booking.id,
            booking.person_id,
            person.name,
        )
        return BookingCreateOut(
            id=booking.id,
            name=person.name,
            booking_date=booking.booking_date,
            booking_time=booking.booking_time,
            guests=booking.guests,
            status=booking.status,
        )
    except HTTPException as e:
        main_log.exception("Ошибка при обработке POST /bookings: %s", e)
        raise
