import logging.config

from core import dict_config
from database import BookingStatus, get_db
from fastapi import APIRouter, Depends, HTTPException, status
from schemas import BookingCreateIn, BookingCreateOut
from services import add_new_booking
from sqlalchemy.ext.asyncio import AsyncSession

logging.config.dictConfig(dict_config)

main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)


router = APIRouter()


@router.post(
    "/bookings",
    response_model=BookingCreateOut,
    status_code=status.HTTP_201_CREATED,
)
async def new_booking(
    information_booking: BookingCreateIn,
    db: AsyncSession = Depends(get_db),
):
    """
    Создаёт новое бронирование.

    Args:
        information_booking (BookingCreateIn): Данные для создания брони.
            Ожидает поля бронирования, включая имя человека, телефон,
            дату бронирования, время бронирования и количество гостей.
        db (AsyncSession): Асинхронная SQLAlchemy-сессия, получаемая через Depends(get_db).

    Returns:
        BookingCreateOut: Созданная бронь, включая:
            - id: ID брони
            - name: имя человека
            - booking_date: дата бронирования
            - booking_time: время бронирования
            - guests: количество гостей
            - status: статус брони

    Raises:
        HTTPException: 500, если произошла непредвиденная ошибка сервера.
    """
    main_log.debug("Начало обработки POST /bookings")
    main_log.info("Получены данные на создание брони")
    try:
        booking, person = await add_new_booking(
            information_booking=information_booking, db=db
        )
        main_log.info(
            "Бронь успешно создана: booking_id=%s, person_id=%s, name=%s",
            booking.id,
            person.id,
            person.name,
        )
        return BookingCreateOut(
            id=booking.id,
            name=person.name,
            booking_date=booking.booking_date,
            booking_time=booking.booking_time,
            guests=booking.guests,
            status=BookingStatus.active ,
        )

    except HTTPException as e:
        main_log.exception("Ошибка при обработке POST /bookings: %s", e)
        raise
