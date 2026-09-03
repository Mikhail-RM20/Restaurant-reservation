from .delete_bookings_by_id import router as delete_bookings_by_id_router
from .get_booking_by_id import router as booking_by_id_router
from .get_list_bookings import router as list_bookings_router
from .route_new_booking import router as new_booking_router

__all__ = [
    "new_booking_router",
    "list_bookings_router",
    "booking_by_id_router",
    "delete_bookings_by_id_router",
]
