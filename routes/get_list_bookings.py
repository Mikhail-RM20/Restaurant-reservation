import logging.config
from datetime import date
from typing import Optional

from core import dict_config
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from services import get_information_about_bookings
from schemas import BookingCreateOut
from sqlalchemy.ext.asyncio import AsyncSession

logging.config.dictConfig(dict_config)

main_log = logging.getLogger("route_logger")
main_log.setLevel(logging.DEBUG)

router = APIRouter()


@router.get(
    "/bookings",
    response_model=list[BookingCreateOut],
    status_code=status.HTTP_200_OK,
)
async def get_bookings(
    date: Optional[date] = Query(
        default=None,
        description="Фильтр по дате (YYYY-MM-DD)",
        examples=["2026-09-10"],
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Возвращает список бронирований.

    Args:
        date (Optional[date]): Необязательная дата фильтрации.
            Если передана, возвращаются брони только на эту дату.
            Если не передана, возвращаются все брони.
        db (AsyncSession): Асинхронная SQLAlchemy-сессия, получаемая через Depends(get_db).

    Returns:
        list[BookingCreateOut] | str: Список бронирований в формате BookingCreateOut.
            Если бронирований нет, возвращается строка с сообщением об отсутствии записей.

    Raises:
        HTTPException: 500, если произошла непредвиденная ошибка сервера.
    """
    main_log.debug(
        "Начало обработки GET /bookings с параметром booking_date=%s",
        date,
    )
    try:
        main_log.info(
            "Запрос списка бронирований, фильтр по дате=%s",
            date,
        )
        result_get_bookings = await get_information_about_bookings(
            booking_date=date, db=db
        )

        if not result_get_bookings:
            main_log.info(
                "Бронирования не найдены для booking_date=%s",
                date,
            )
            return []

        else:
            return [
                BookingCreateOut(
                    id=booking.id,
                    name=person.name,
                    phone=person.phone,
                    booking_date=booking.booking_date,
                    booking_time=booking.booking_time,
                    guests=booking.guests,
                    status=booking.status,
                )
                for booking, person in result_get_bookings
            ]

    except HTTPException as e:
        main_log.exception("Ошибка при обработке POST /bookings: %s", e)
        raise
