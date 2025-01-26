import csv
import json
import logging
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from pprint import pprint
from typing import Any

import firebase_admin.auth
import pydantic
from google.cloud import firestore
from typer import Option, Typer

from lta.api.configuration import (
    Environment,
    get_assignment_repository,
    get_assignment_service,
    get_expo_notification_publisher,
    get_firebase_app,
    get_firestore_client,
    get_mailgun_notification_publisher,
    get_schedule_repository,
    get_scheduler_service,
    get_survey_repository,
    get_user_repository,
    get_vonage_notification_publisher,
    set_environment,
)
from lta.authentication import HAS_SET_OWN_PASSWORD_FIELD
from lta.domain.assignment import Assignment
from lta.domain.survey import Survey
from lta.domain.survey_repository import SurveyCreation

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
def remove_has_set_own_password(
    user_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    app = get_firebase_app()
    custom_claims = firebase_admin.auth.get_user(user_id, app).custom_claims
    if custom_claims is None:
        custom_claims = dict()
    custom_claims[HAS_SET_OWN_PASSWORD_FIELD] = False
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


@app.command()
def send_test_sms_notification(
    user_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    notification_publisher = get_vonage_notification_publisher()
    user_repository = get_user_repository()

    phone_number = user_repository.get_user(user_id).notification_info.phone_number
    if phone_number is None:
        print(f"No notification phone number found for user id: {user_id}")
        return

    notification_publisher.send_sms(
        phone_number=phone_number,
        message="Test SMS Notification",
    )


@app.command()
def send_test_push_notification(
    user_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    notification_publisher = get_expo_notification_publisher()
    user_repository = get_user_repository()

    devices = user_repository.get_user(user_id).notification_info.devices
    tokens = [device.token for device in devices if device.token != "__null__"]
    if len(tokens) == 0:
        print(f"No device token found for user id: {user_id}")
        return

    for token in tokens:
        print(f"Sending push notification to device token: {token}")
        notification_publisher.send_push_notification(
            device_token=token,
            title="LTA test notification",
            body="This is a test push notification.",
        )


@app.command()
def export_csv(
    user_ids: list[str] = Option(..., "--user-id", help="may be repeated"),
    file: Path = Option(..., help="path to the output CSV file"),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    user_repository = get_user_repository()
    assignment_repository = get_assignment_repository()
    survey_repository = get_survey_repository()

    assignment_data: list[dict[str, Any]] = []
    surveys = {survey.id: survey for survey in survey_repository.list_surveys()}

    for user_id in user_ids:
        user = user_repository.get_user(user_id)
        for assignment in assignment_repository.list_assignments(user_id=user.id):
            assignment_data.append(
                convert_assignment_to_dict(assignment, surveys[assignment.survey_id])
            )

    if len(assignment_data) == 0:
        print("No assignments found for the given user ids.")
        return

    with file.open("w", newline="") as csvfile:
        headers: list[str] = []
        header_set: set[str] = set()
        for a in assignment_data:
            for k in a.keys():
                if k not in header_set:
                    headers.append(k)
                    header_set.add(k)
        csv_writer = csv.DictWriter(csvfile, fieldnames=headers)
        csv_writer.writeheader()
        csv_writer.writerows(assignment_data)


def convert_assignment_to_dict(
    assignment: Assignment, survey: Survey
) -> dict[str, Any]:
    if assignment.submitted_at and assignment.opened_at:

        def compare(dt: datetime) -> bool:
            assert assignment.submitted_at is not None
            return dt < assignment.submitted_at

        opened_at: datetime = next(filter(compare, assignment.opened_at[::-1]))
        time_to_answer = (assignment.submitted_at - opened_at).total_seconds()
    else:
        time_to_answer = None

    data = dict(
        id=assignment.id,
        user_id=assignment.user_id,
        survey_id=assignment.survey_id,
        submitted_at=assignment.submitted_at,
        created_at=assignment.created_at,
        expired_at=assignment.expired_at,
        last_notified_at=(
            assignment.notified_at[-1].isoformat() if assignment.notified_at else None
        ),
        number_of_notifications=len(assignment.notified_at),
        last_opened_at=(
            assignment.opened_at[-1].isoformat() if assignment.opened_at else None
        ),
        number_of_openings=len(assignment.opened_at),
        has_answers=assignment.answers is not None,
        time_to_answer_from_creation=(
            (assignment.submitted_at - assignment.created_at).total_seconds()
            if assignment.submitted_at
            else None
        ),
        time_to_answer=time_to_answer,
    )
    if assignment.answers is None:
        return data

    for question, answer in zip(survey.questions, assignment.answers):
        if question.type == "single-choice":
            assert isinstance(answer, int)
            data[question.message] = question.choices[answer]
        elif question.type == "multiple-choice":
            assert isinstance(answer, list)
            data[question.message] = "\n".join(question.choices[i] for i in answer)
        elif question.type == "open-ended":
            assert isinstance(answer, str)
            data[question.message] = answer

    return data


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.timestamp()
        return super().default(o)


@app.command()
def backup_database(
    output_dir: Path = Option(..., help="path to the output directory"),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    _check_directory_is_empty(output_dir)
    client = get_firestore_client()
    _backup_surveys(client, output_dir / "surveys.json")
    _backup_users(client, output_dir / "users.json")
    _backup_assignments(client, output_dir / "assignments.json")


def _check_directory_is_empty(directory: Path) -> None:
    if not directory.exists():
        raise RuntimeError(f"Directory '{directory}' does not exist.")
    if not directory.is_dir():
        raise RuntimeError(f"'{directory}' is not a directory.")
    if len(list(directory.iterdir())) > 0:
        raise RuntimeError(f"Directory '{directory}' is not empty.")


def _backup_surveys(client: firestore.Client, output_file: Path) -> None:
    docs = client.collection("surveys").stream()
    data = {doc.id: doc.to_dict() for doc in docs}
    with output_file.open("w") as fh:
        json.dump(data, fh, indent=2)


def _backup_users(client: firestore.Client, output_file: Path) -> None:
    docs = client.collection("users").stream()
    data = {doc.id: doc.to_dict() for doc in docs}
    with output_file.open("w") as fh:
        json.dump(data, fh, indent=2, cls=CustomJSONEncoder)


def _backup_assignments(client: firestore.Client, output_file: Path) -> None:
    data: dict[str, dict[str, Any]] = defaultdict(dict)
    for user_doc in client.collection("users").stream():
        docs = user_doc.reference.collection("assignments").stream()
        data[user_doc.id] = {doc.id: doc.to_dict() for doc in docs}
    with output_file.open("w") as fh:
        json.dump(data, fh, indent=2, cls=CustomJSONEncoder)


@app.command()
def clone_survey(
    survey_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    survey_repository = get_survey_repository()
    survey_to_clone = survey_repository.get_survey(survey_id)
    survey = SurveyCreation(
        title=survey_to_clone.title,
        welcome_message=survey_to_clone.welcome_message,
        submit_message=survey_to_clone.submit_message,
        questions=survey_to_clone.questions,
        notifications=survey_to_clone.notifications,
    )
    id = str(uuid.uuid4())
    survey_repository.create_survey(
        id=id,
        survey=survey,
    )

    print("Survey cloned successfully with id:", id)


@app.command()
def create_survey_from_file(
    input_file: Path = Option(..., help="path to the input JSON file"),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    data = json.load(input_file.open())
    survey = pydantic.TypeAdapter(SurveyCreation).validate_python(data)
    survey_repository = get_survey_repository()
    id = str(uuid.uuid4())
    survey_repository.create_survey(
        id=id,
        survey=survey,
    )
    print("Survey created successfully with id:", id)


@app.command()
def export_completed_assigned_surveys(
    user_ids: list[str] = Option(..., "--user-id", help="may be repeated"),
    file: Path = Option(..., help="path to the output CSV file"),
    use_email_address: bool = Option(
        False, help="use email addresses instead of user ids"
    ),
) -> None:
    """
    Produce a CSV file containing a list of all assignments for the given user ids,
    and if these assignments are completed.

        ,       2024-01-01, 2024-01-02, 2024-01-03, 2024-01-04
        user1,  X,        ,           , X         , X
        user2,  ,         , X         ,           , X

    NOTE: This command assumes that there is only one assignment per user per day.
    """
    set_environment(Environment.LOCAL_PROD)
    user_repository = get_user_repository()
    assignment_repository = get_assignment_repository()

    assignments: list[Assignment] = []
    id2addresses = dict()
    for user_id in user_ids:
        user = user_repository.get_user(user_id)
        id2addresses[user.id] = user.email_address
        for assignment in assignment_repository.list_assignments(user_id=user.id):
            assignments.append(assignment)

    dates = sorted(set(a.created_at.strftime("%Y-%m-%d") for a in assignments))
    data: dict[str, dict[str, bool]] = {
        user_id: {date: False for date in dates} for user_id in user_ids
    }

    for assignment in assignments:
        data[assignment.user_id][assignment.created_at.strftime("%Y-%m-%d")] = (
            assignment.submitted_at is not None
        )

    with file.open("w", newline="") as csvfile:
        headers: list[str] = ["user"] + [date for date in dates]
        csv_writer = csv.DictWriter(csvfile, fieldnames=headers)
        csv_writer.writeheader()
        for user_id, row in data.items():
            csv_writer.writerow(
                dict(user=id2addresses[user_id] if use_email_address else user_id)
                | {date: "x" if value else "" for date, value in row.items()}
            )


if __name__ == "__main__":
    app()
