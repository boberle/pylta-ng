import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import firebase_admin.auth
from typer import Option, Typer

from lta.api.configuration import (
    Environment,
    get_assignment_service,
    get_firebase_app,
    get_survey_repository,
    get_user_repository,
    set_environment,
)
from lta.authentication import HAS_SET_OWN_PASSWORD_FIELD
from lta.domain.survey_repository import SurveyCreation

app = Typer()


@app.command()
def add_surveys(
    source: Path = Option(
        Path("testdata/surveys.json"), help="path to the source JSON file"
    ),
) -> None:
    set_environment(Environment.LOCAL_DEV)
    surveys = json.load(source.open())
    survey_repository = get_survey_repository()
    for survey in surveys:
        survey_repository.create_survey(survey["id"], SurveyCreation(**survey))


@app.command()
def list_surveys() -> None:
    set_environment(Environment.LOCAL_DEV)
    survey_repository = get_survey_repository()
    for survey in survey_repository.list_surveys():
        print(survey)


@app.command()
def schedule_assignment(
    user_id: str = Option(...),
    survey_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_DEV)
    assignment_service = get_assignment_service()
    ref_time = datetime.now(tz=timezone.utc)
    assignment_service.create_assignment(
        user_id=user_id, survey_id=survey_id, ref_time=ref_time
    )


@app.command()
def create_user() -> None:
    set_environment(Environment.LOCAL_DEV)
    user_repository = get_user_repository()
    id = str(uuid.uuid4())
    print(f"Generated new user id: {id}")
    user_repository.create_user(
        id,
        "foo@idontexist.net",
        datetime.now(tz=timezone.utc),
    )


@app.command()
def print_assignment_answers(
    user_id: str = Option(...),
    assignment_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_DEV)
    assignment_service = get_assignment_service()
    assignment = assignment_service.assignment_repository.get_assignment(
        user_id, assignment_id
    )
    if assignment.answers is None:
        print("No answers")
    else:
        for i, answer in enumerate(assignment.answers):
            print(i, answer.model_dump() if answer is not None else "---")


@app.command()
def create_firebase_auth_user(
    email_address: str = Option("a@b.com"),
    password: str = Option("abcdef"),
    is_admin: bool = Option(True),
    has_set_own_password: bool = Option(True),
) -> None:
    set_environment(Environment.LOCAL_DEV)
    app = get_firebase_app()

    user = firebase_admin.auth.create_user(
        app=app,
        email=email_address,
        password=password,
    )
    custom_claims = user.custom_claims

    if is_admin or has_set_own_password:
        if custom_claims is None:
            custom_claims = dict()
        if is_admin:
            custom_claims["admin"] = True
        if has_set_own_password:
            custom_claims[HAS_SET_OWN_PASSWORD_FIELD] = True
        firebase_admin.auth.set_custom_user_claims(
            user.uid, custom_claims=custom_claims, app=app
        )


if __name__ == "__main__":
    app()
