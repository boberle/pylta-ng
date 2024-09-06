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
    OpenEndedQuestion,
    SingleChoiceQuestion,
    Survey,
)
from lta.domain.survey_repository import SurveyRepository
from lta.infra.repositories.firestore.survey_repository import FirestoreSurveyRepository
from lta.infra.repositories.memory.survey_repository import InMemorySurveyRepository


@pytest.fixture()
def prefilled_memory_survey_repository() -> InMemorySurveyRepository:
    return InMemorySurveyRepository(
        {
            "survey1": Survey(
                id="survey1",
                title="Sample first survey!",
                welcome_message="Welcome to our survey!",
                submit_message="Thank you for your participation!",
                publish_notification=NotificationMessage(
                    title="Hey", message="Survey published!"
                ),
                soon_to_expire_notification=NotificationMessage(
                    title="Hey", message="Survey soon to expire!"
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
            ),
            "survey2": Survey(
                id="survey2",
                title="Sample second survey!",
                welcome_message="Welcome to our second survey!",
                submit_message="Thank you for your participation!",
                publish_notification=NotificationMessage(
                    title="Hi", message="A second survey is published!"
                ),
                soon_to_expire_notification=NotificationMessage(
                    title="Hi", message="The second survey is soon to expire!"
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
            ),
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
    return InMemorySurveyRepository(surveys={})


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
