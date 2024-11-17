import urllib.request
from typing import Any, Generator

import pytest

from lta.api.configuration import (
    get_firebase_app,
    get_firestore_client,
    get_project_name,
)
from lta.domain.survey import (
    MultipleChoiceQuestion,
    NotificationMessage,
    NotificationSet,
    OpenEndedQuestion,
    SingleChoiceQuestion,
    Survey,
    SurveyNotificationInfo,
)
from lta.domain.survey_repository import SurveyRepository
from lta.infra.repositories.firestore.survey_repository import FirestoreSurveyRepository
from lta.infra.repositories.memory.survey_repository import InMemorySurveyRepository


@pytest.fixture()
def sample_survey_1() -> Survey:
    return Survey(
        id="survey1",
        title="Sample first survey!",
        welcome_message="Welcome to our survey!",
        submit_message="Thank you for your participation!",
        notifications=SurveyNotificationInfo(
            email_notification=NotificationSet(
                initial_notification=NotificationMessage(
                    title="Hey", message="Initial email notification!"
                ),
                reminder_notification=NotificationMessage(
                    title="Hey", message="Reminder email notification!"
                ),
            ),
            sms_notification=NotificationSet(
                initial_notification=NotificationMessage(
                    title="", message="Initial SMS notification!"
                ),
                reminder_notification=NotificationMessage(
                    title="", message="Reminder SMS notification!"
                ),
            ),
        ),
        questions=[
            SingleChoiceQuestion(
                message="What is your favorite color?",
                choices=["Red", "Blue", "Green", "Yellow"],
            ),
            SingleChoiceQuestion(
                message="What is your favorite music genre?",
                choices=["Rock", "Pop", "Hip-hop", "Jazz"],
            ),
            MultipleChoiceQuestion(
                message="What are your favorite fruits?",
                choices=["Apple", "Banana", "Orange", "Pineapple"],
            ),
            OpenEndedQuestion(
                message="Tell us about your travel experiences.",
            ),
        ],
    )


@pytest.fixture()
def sample_survey_2() -> Survey:
    return Survey(
        id="survey2",
        title="Sample second survey!",
        welcome_message="Welcome to our second survey!",
        submit_message="Thank you for your participation!",
        notifications=SurveyNotificationInfo(
            email_notification=NotificationSet(
                initial_notification=NotificationMessage(
                    title="Hey", message="Initial email notification!"
                ),
                reminder_notification=NotificationMessage(
                    title="Hey", message="Reminder email notification!"
                ),
            )
        ),
        questions=[
            SingleChoiceQuestion(
                message="What is your favorite animal?",
                choices=["Dog", "Cat", "Bird", "Fish"],
            ),
            MultipleChoiceQuestion(
                message="What are your favorite books?",
                choices=[
                    "To Kill a Mockingbird",
                    "1984",
                    "Pride and Prejudice",
                    "The Great Gatsby",
                ],
            ),
            MultipleChoiceQuestion(
                message="What are your favorite movies?",
                choices=[
                    "The Shawshank Redemption",
                    "The Godfather",
                    "Pulp Fiction",
                    "The Dark Knight",
                ],
            ),
            OpenEndedQuestion(
                message="Tell us about your favorite movies.",
            ),
        ],
    )


@pytest.fixture()
def prefilled_memory_survey_repository(
    sample_survey_1: Survey,
    sample_survey_2: Survey,
) -> InMemorySurveyRepository:
    return InMemorySurveyRepository(
        {
            "survey1": sample_survey_1,
            "survey2": sample_survey_2,
        }
    )


@pytest.fixture
def empty_firestore_survey_repository() -> Generator[SurveyRepository, None, None]:
    # TODO: factor
    get_firebase_app()
    yield FirestoreSurveyRepository(get_firestore_client(use_emulator=True))
    request = urllib.request.Request(
        f"http://localhost:8080/emulator/v1/projects/{get_project_name()}/databases/(default)/documents",
        method="DELETE",
    )
    resp = urllib.request.urlopen(request)
    if resp.status != 200:
        raise RuntimeError("Failed to delete Firestore emulator data")


@pytest.fixture
def empty_memory_survey_repository() -> SurveyRepository:
    return InMemorySurveyRepository()


@pytest.fixture(params=["memory", "firestore"])
def empty_survey_repository(
    request: Any,
    empty_firestore_survey_repository: FirestoreSurveyRepository,
    empty_memory_survey_repository: InMemorySurveyRepository,
) -> Generator[SurveyRepository, None, None]:
    if request.param == "firestore":
        yield empty_firestore_survey_repository
    else:
        yield empty_memory_survey_repository
