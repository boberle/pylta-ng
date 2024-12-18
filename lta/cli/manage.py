import logging
import uuid
from datetime import datetime, timezone
from pprint import pprint

import firebase_admin.auth
from typer import Option, Typer

from lta.api.configuration import (
    Environment,
    get_assignment_repository,
    get_assignment_service,
    get_firebase_app,
    get_mailgun_notification_publisher,
    get_schedule_repository,
    get_scheduler_service,
    get_survey_repository,
    get_user_repository,
    set_environment,
)
from lta.authentication import HAS_SET_OWN_PASSWORD_FIELD

logging.basicConfig(level=logging.DEBUG)


app = Typer(pretty_exceptions_enable=False)


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


@app.command()
def schedule_assignments(
    ref_time: datetime = Option(
        datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    ),
) -> None:
    """Schedule assignments for the ref date"""
    set_environment(Environment.LOCAL_PROD)
    service = get_scheduler_service()
    service.schedule_assignments(ref_time=ref_time)


@app.command()
def send_test_email_notification(
    user_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    email_notification_publisher = get_mailgun_notification_publisher()
    user_repository = get_user_repository()

    notification_email = user_repository.get_user(
        user_id
    ).notification_info.email_address
    if notification_email is None:
        print(f"No notification email found for user id: {user_id}")
        return

    email_notification_publisher.send_email(
        recipient_email=notification_email,
        subject="Test Email Notification",
        body="This is a test email notification.",
    )


@app.command()
def schedule_assignment(
    user_id: str = Option(...),
    survey_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    assignment_service = get_assignment_service()
    ref_time = datetime.now(tz=timezone.utc)
    assignment_service.create_assignment(
        user_id=user_id, survey_id=survey_id, ref_time=ref_time
    )


@app.command()
def create_user(
    id: str | None = Option(None),
    email_address: str = Option(...),
    notification_email: str | None = Option(None),
    phone_number: str | None = Option(None),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    user_repository = get_user_repository()
    if id is None:
        id = str(uuid.uuid4())
        print(f"Generated new user id: {id}")
    user_repository.create_user(
        id,
        email_address,
        datetime.now(tz=timezone.utc),
        notification_email=notification_email,
        phone_number=phone_number,
    )


@app.command()
def check_model_parsing() -> None:
    set_environment(Environment.LOCAL_PROD)

    print("Checking users and assignments...")
    user_repository = get_user_repository()
    assignment_repository = get_assignment_repository()
    for user in user_repository.list_users():
        print(f"User: {user.id}... ok")
        for assignment in assignment_repository.list_assignments(user_id=user.id):
            print(f"Assignment: {assignment.id}... ok")

    print("Checking surveys...")
    survey_repository = get_survey_repository()
    for survey in survey_repository.list_surveys():
        print(f"Survey: {survey.id}... ok")

    print("Checking schedules...")
    schedule_repository = get_schedule_repository()
    for schedule in schedule_repository.list_schedules():
        print(f"Schedule: {schedule.id}... ok")


@app.command()
def stats() -> None:
    set_environment(Environment.LOCAL_PROD)

    user_repository = get_user_repository()
    assignment_repository = get_assignment_repository()
    for user in user_repository.list_users():
        total = 0
        submitted = 0
        for assignment in assignment_repository.list_assignments(user_id=user.id):
            total += 1
            if assignment.submitted_at is not None:
                submitted += 1
        print(f"User: {user.id} - {user.email_address}: {submitted} / {total}")


if __name__ == "__main__":
    app()
