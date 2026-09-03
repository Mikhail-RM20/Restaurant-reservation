from contextlib import asynccontextmanager

from database import Base, engine
from fastapi import FastAPI
from routes import (
    booking_by_id_router,
    delete_bookings_by_id_router,
    list_bookings_router,
    new_booking_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(new_booking_router)
app.include_router(list_bookings_router)
app.include_router(booking_by_id_router)
app.include_router(delete_bookings_by_id_router)
