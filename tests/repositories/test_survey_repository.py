import pytest

from lta.domain.survey import (
    MultipleChoiceQuestion,
    NotificationMessage,
    NotificationSet,
    OpenEndedQuestion,
    SingleChoiceQuestion,
    Survey,
    SurveyNotificationInfo,
)
from lta.domain.survey_repository import (
    SurveyCreation,
    SurveyNotFound,
    SurveyRepository,
)


def test_get_survey__with_all_properties(
    empty_survey_repository: SurveyRepository,
) -> None:
    survey_id = "1"
    survey_creation = SurveyCreation(
        title="Test Survey",
        welcome_message="Welcome!",
        submit_message="Thank you!",
        questions=[
            SingleChoiceQuestion(message="Favorite color?", choices=["Red", "Blue"]),
            MultipleChoiceQuestion(
                message="Favorite books?", choices=["Book 1", "Book 2"]
            ),
            OpenEndedQuestion(message="Tell us about your favorite color."),
        ],
        notification_info=SurveyNotificationInfo(
            email_notification=NotificationSet(
                initial_notification=NotificationMessage(
                    title="Initial Email",
                    message="This is an initial email notification.",
                ),
                reminder_notification=NotificationMessage(
                    title="Reminder Email",
                    message="This is a reminder email notification.",
                ),
            ),
            sms_notification=NotificationSet(
                initial_notification=NotificationMessage(
                    title="Initial SMS", message="This is an initial SMS notification."
                ),
                reminder_notification=NotificationMessage(
                    title="Reminder SMS", message="This is a reminder SMS notification."
                ),
            ),
        ),
    )
    empty_survey_repository.create_survey(survey_id, survey_creation)

    survey = empty_survey_repository.get_survey(survey_id)
    assert survey.id == survey_id
    assert survey == Survey(
        id=survey_id,
        **survey_creation.model_dump(),
    )


def test_get_survey_not_found(empty_survey_repository: SurveyRepository) -> None:
    with pytest.raises(SurveyNotFound):
        empty_survey_repository.get_survey("non_existent_id")


def test_list_surveys(empty_survey_repository: SurveyRepository) -> None:
    survey_id_1 = "1"
    survey_creation_1 = SurveyCreation(
        title="Survey 1",
        welcome_message="Welcome 1!",
        submit_message="Thanks 1!",
        questions=[],
    )
    survey_id_2 = "2"
    survey_creation_2 = SurveyCreation(
        title="Survey 2",
        welcome_message="Welcome 2!",
        submit_message="Thanks 2!",
        questions=[],
    )
    empty_survey_repository.create_survey(survey_id_1, survey_creation_1)
    empty_survey_repository.create_survey(survey_id_2, survey_creation_2)

    surveys = empty_survey_repository.list_surveys()
    assert len(surveys) == 2
    assert surveys[0] == Survey(
        id=survey_id_1,
        **survey_creation_1.model_dump(),
    )
    assert surveys[1] == Survey(
        id=survey_id_2,
        **survey_creation_2.model_dump(),
    )
