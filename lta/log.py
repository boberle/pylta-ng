import google.cloud.logging


def setup_logging() -> None:
    google.cloud.logging.Client().setup_logging()  # type:ignore
