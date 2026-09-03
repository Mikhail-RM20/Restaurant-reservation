dict_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "base": {
            "format": "%(asctime)s | %(name)s | %(levelname)s |"
            " %(message)s | %(lineno)d",
        }
    },
    "handlers": {
        "file_bookings": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "base",
            "filename": "file_booking.log",
            "mode": "a",
            "encoding": "utf-8",
        },
        "file_services": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "base",
            "filename": "file_service.log",
            "mode": "a",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "route_logger": {"level": "DEBUG", "handlers": ["file_bookings"]},
        "services_logger": {"level": "DEBUG", "handlers": ["file_services"]},
    },
}
