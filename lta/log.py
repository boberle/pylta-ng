import google.cloud.logging


def setup_google_cloud_logging() -> None:
    google.cloud.logging.Client().setup_logging()  # type:ignore
