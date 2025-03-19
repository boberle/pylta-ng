from typing import Literal

from pydantic import BaseModel, Field


class Question(BaseModel):
    message: str
    conditions: dict[int, None] = Field(default_factory=dict)


class SingleChoiceQuestion(Question):
    type: Literal["single-choice"] = "single-choice"
    choices: list[str]
    last_is_specify: bool = False


class MultipleChoiceQuestion(Question):
    type: Literal["multiple-choice"] = "multiple-choice"
    choices: list[str]
    last_is_specify: bool = False


class OpenEndedQuestion(Question):
    type: Literal["open-ended"] = "open-ended"
    max_length: int = 200
    optional: bool = False


class NotificationMessage(BaseModel):
    title: str
    message: str


class NotificationSet(BaseModel):
    initial_notification: NotificationMessage
    reminder_notification: NotificationMessage


class SurveyNotificationInfo(BaseModel):
    email_notification: NotificationSet | None = None
    sms_notification: NotificationSet | None = None
    push_notification: NotificationSet | None = None


class Survey(BaseModel):
    id: str
    title: str
    welcome_message: str
    submit_message: str
    questions: list[SingleChoiceQuestion | MultipleChoiceQuestion | OpenEndedQuestion]
    notifications: SurveyNotificationInfo = Field(
        default_factory=SurveyNotificationInfo
    )


def get_test_survey() -> Survey:
    return Survey(
        id="test-survey",
        title="Test Survey",
        welcome_message="Welcome to the test survey!",
        submit_message="Thank you for completing the test survey!",
        questions=[
            SingleChoiceQuestion(
                message="What is your favorite color?",
                choices=["Red", "Green", "Blue", "Other (please specify)"],
                last_is_specify=True,
            ),
            MultipleChoiceQuestion(
                message="What are your favorite animals?",
                choices=["Cat", "Dog", "Giraffe", "Fish", "Bird"],
            ),
            OpenEndedQuestion(
                message="What is your favorite flower (optional)?",
                max_length=25,
                optional=True,
            ),
        ],
        notifications=SurveyNotificationInfo(
            email_notification=NotificationSet(
                initial_notification=NotificationMessage(
                    title="Test Survey",
                    message="Test survey at https://langtrackapp.com/panelist/{user_id}/{survey_id}/",
                ),
                reminder_notification=NotificationMessage(
                    title="Reminder: Test Survey",
                    message="Test survey at https://langtrackapp.com/panelist/{user_id}/{survey_id}/",
                ),
            ),
            sms_notification=NotificationSet(
                initial_notification=NotificationMessage(
                    title="",
                    message="Test survey at https://langtrackapp.com/panelist/{user_id}/{survey_id}/",
                ),
                reminder_notification=NotificationMessage(
                    title="",
                    message="Test survey at https://langtrackapp.com/panelist/{user_id}/{survey_id}/",
                ),
            ),
            push_notification=NotificationSet(
                initial_notification=NotificationMessage(
                    title="LTA Survey published",
                    message="Hey! New survey available!",
                ),
                reminder_notification=NotificationMessage(
                    title="LTA Survey waiting for you",
                    message="Don't forget to take the survey soon!",
                ),
            ),
        ),
    )
