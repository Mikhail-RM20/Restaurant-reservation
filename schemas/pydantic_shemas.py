from datetime import date, datetime, time, timedelta

from database import BookingStatus
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

BOOKING_TIMES = {
    time(12, 0),
    time(13, 0),
    time(14, 0),
    time(15, 0),
    time(16, 0),
    time(17, 0),
    time(18, 0),
    time(19, 0),
    time(20, 0),
    time(21, 0),
    time(22, 0),
}


class BookingCreateIn(BaseModel):
    name: str = Field(
        ...,
        title="Имя человека. / Name person.",
        examples=["Максим"],
        min_length=2,
        pattern=r"^[A-Za-zА-Яа-яЁё\s-]+$",
    )
    phone: str = Field(
        ...,
        title="Номер телефона человека. / Phone number person.",
        description="Номер телефона человека для создания брони. / The person’s phone number for making a reservation. ",
        pattern=r"^(?:\+7|8)\d{10}$",
    )
    booking_date: date = Field(
        ...,
        title="Дата бронирования / Booking date",
    )

    @field_validator("booking_date")
    @classmethod
    def validate_booking_date(cls, v: date) -> date:
        today = date.today()
        max_date = today + timedelta(days=90)
        if v < today:
            raise ValueError(
                "Дата бронирования должна быть сегодня или позже. / Booking date must be today or later."
            )
        if v > max_date:
            raise ValueError(
                "Дата бронирования должна быть не позднее, чем через 90 дней с сегодняшнего дня. / "
                "Booking date must not be later than 90 days from today."
            )
        return v

    booking_time: time = Field(..., description="Время брони")

    @field_validator("booking_time")
    @classmethod
    def validate_booking_time(cls, v: time) -> time:
        if v not in BOOKING_TIMES:
            raise ValueError(
                "Время бронирования должно быть одним из 12:00, 13:00, ..., 22:00. / Booking time must be "
                "one of: 12:00, 13:00, "
                "..., 22:00"
            )
        return v

    @model_validator(mode="after")
    def validate_booking_datetime(self):
        now = datetime.now()
        booking_dt = datetime.combine(self.booking_date, self.booking_time)

        if self.booking_date == now.date() and booking_dt < now:
            raise ValueError(
                "Вы не можете забронировать время в прошлом на сегодняшний день./ You cannot book a time "
                "in the past for today"
            )

        return self

    guests: int = Field(
        ...,
        title="Кол-во гостей. / Number of guests.",
        description="Кол-во персон, для которых подготовить столик. / The number of people for whom to prepare a table.",
        ge=1,
        le=12,
    )


class BookingCreateOut(BookingCreateIn):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int = Field(
        ...,
        title="ID-брони. / ID‑booking.",
        description="ID бронирования, которое выбрал пользователь. / The booking ID that the user selected.",
    )
    status: BookingStatus = Field(
        ...,
        title="Статус брони. / Booking status",
    )  # Берем из базы
