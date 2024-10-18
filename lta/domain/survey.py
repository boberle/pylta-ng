from typing import Literal

from pydantic import BaseModel


class Question(BaseModel):
    message: str


class SingleChoiceQuestion(Question):
    type: Literal["single-choice"] = "single-choice"
    choices: list[str]


class MultipleChoiceQuestion(Question):
    type: Literal["multiple-choice"] = "multiple-choice"
    choices: list[str]


class OpenEndedQuestion(Question):
    type: Literal["open-ended"] = "open-ended"
    max_length: int = 200


class NotificationMessage(BaseModel):
    title: str
    message: str


class Survey(BaseModel):
    id: str
    title: str
    welcome_message: str
    submit_message: str
    publish_notification: NotificationMessage
    soon_to_expire_notification: NotificationMessage
    questions: list[SingleChoiceQuestion | MultipleChoiceQuestion | OpenEndedQuestion]


def get_test_survey() -> Survey:
    return Survey(
        id="test-survey",
        title="Test Survey",
        welcome_message="Welcome to the test survey!",
        submit_message="Thank you for completing the test survey!",
        publish_notification=NotificationMessage(
            title="Hi", message="The test survey is now available!"
        ),
        soon_to_expire_notification=NotificationMessage(
            title="Hi", message="The test survey is soon to expire!"
        ),
        questions=[
            SingleChoiceQuestion(
                message="What is your favorite animal?",
                choices=["Dog", "Cat", "Bird", "Fish"],
            ),
            MultipleChoiceQuestion(
                message="What are your favorite fruit?",
                choices=["Apple", "Banana", "Orange", "Grape"],
            ),
            OpenEndedQuestion(
                message="What is your favorite color?",
                max_length=25,
            ),
        ],
    )
