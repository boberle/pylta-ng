import uuid
from datetime import date, datetime, timezone
from pprint import pprint

import firebase_admin.auth
from typer import Option, Typer

from lta.api.configuration import (
    Environment,
    get_email_notification_publisher,
    get_firebase_app,
    get_scheduler_service,
    get_user_repository,
    set_environment,
)
from lta.authentication import HAS_SET_OWN_PASSWORD_FIELD
from lta.domain.scheduler.notification_pulisher import Notification

app = Typer()


@app.command()
def set_admin(
    user_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    app = get_firebase_app()
    custom_claims = firebase_admin.auth.get_user(user_id, app).custom_claims
    if custom_claims is None:
        custom_claims = dict()
    custom_claims["admin"] = True
    firebase_admin.auth.set_custom_user_claims(
        user_id, custom_claims=custom_claims, app=app
    )


@app.command()
def set_has_set_own_password(
    user_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    app = get_firebase_app()
    custom_claims = firebase_admin.auth.get_user(user_id, app).custom_claims
    if custom_claims is None:
        custom_claims = dict()
    custom_claims[HAS_SET_OWN_PASSWORD_FIELD] = True
    firebase_admin.auth.set_custom_user_claims(
        user_id, custom_claims=custom_claims, app=app
    )


@app.command()
def get_claims(
    user_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    app = get_firebase_app()
    custom_claims = firebase_admin.auth.get_user(user_id, app).custom_claims
    pprint(custom_claims)


def date_parser(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


@app.command()
def schedule_assignments(
    ref_date: date = Option(
        datetime.now(tz=timezone.utc).date().strftime("%Y-%m-%d"), parser=date_parser
    ),
) -> None:
    """Schedule assignments for the ref date"""
    set_environment(Environment.LOCAL_PROD)
    service = get_scheduler_service()
    service.schedule_assignments_for_date(ref_date=ref_date)


@app.command()
def send_test_email_notification(
    user_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    email_notification_publisher = get_email_notification_publisher()
    user_repository = get_user_repository()

    notification_email = user_repository.get_notification_email(user_id)
    if notification_email is None:
        print(f"No notification email found for user id: {user_id}")
        return

    email_notification_publisher.publish(
        notification_email,
        Notification(
            title="Test Email Notification",
            message="This is a test email notification.",
        ),
    )


@app.command()
def create_user(
    id: str | None = Option(None),
    email_address: str = Option(...),
    notification_email: str | None = Option(None),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    user_repository = get_user_repository()
    if id is None:
        id = str(uuid.uuid4())
    user_repository.create_user(
        id,
        email_address,
        datetime.now(tz=timezone.utc),
        notification_email=notification_email,
    )


if __name__ == "__main__":
    app()
