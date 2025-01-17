import os
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from functools import cache, cached_property
from typing import Literal, Optional
from urllib.parse import urljoin

import firebase_admin
import firebase_admin.firestore
import google.cloud.firestore
import vonage
from google.cloud import tasks_v2
from pydantic import EmailStr, Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from lta.domain.assignment_repository import AssignmentRepository
from lta.domain.group_repository import GroupRepository
from lta.domain.schedule_repository import ScheduleRepository
from lta.domain.scheduler.assignment_scheduler import AssignmentScheduler
from lta.domain.scheduler.assignment_service import AssignmentService
from lta.domain.scheduler.notification_scheduler import NotificationScheduler
from lta.domain.scheduler.notification_service import NotificationService
from lta.domain.scheduler.scheduler_service import SchedulerService
from lta.domain.survey import NotificationMessage
from lta.domain.survey_repository import SurveyRepository
from lta.domain.user_repository import UserRepository
from lta.infra.repositories.firestore.assignment_repository import (
    FirestoreAssignmentRepository,
)
from lta.infra.repositories.firestore.group_repository import FirestoreGroupRepository
from lta.infra.repositories.firestore.schedule_repository import (
    FirestoreScheduleRepository,
)
from lta.infra.repositories.firestore.survey_repository import FirestoreSurveyRepository
from lta.infra.repositories.firestore.user_repository import FirestoreUserRepository
from lta.infra.scheduler.direct.assignment_scheduler import DirectAssignmentScheduler
from lta.infra.scheduler.direct.notification_scheduler import (
    DirectNotificationScheduler,
)
from lta.infra.scheduler.expo.notification_publisher import (
    ExpoAPI,
    ExpoNotificationPublisher,
)
from lta.infra.scheduler.google_tasks.assignment_scheduler import (
    CloudTasksAssignmentScheduler,
)
from lta.infra.scheduler.google_tasks.notification_scheduler import (
    CloudTasksNotificationScheduler,
)
from lta.infra.scheduler.mailgun.notification_publisher import (
    MailgunAPI,
    MailgunNotificationPublisher,
)
from lta.infra.scheduler.vonage.notification_publisher import (
    VonageNotificationPublisher,
)
from lta.infra.tasks_api import CloudTasksAPI


class Settings(BaseSettings):
    PROJECT_NAME: str = "dummy-project"
    PROJECT_LOCATION: str = "europe-west1"
    ALLOWED_ORIGINS: list[str] = Field(default_factory=list)
    ASSIGNMENT_LIMIT_ON_APP_HOME_PAGE: int = 20
    SOON_TO_EXPIRE_NOTIFICATION_DELAYS_MINUTES: list[int] = [60, 120]
    ASSIGNMENT_EXPIRATION_DELAY_HOURS: int = 24
    CLOUD_TASKS_SERVICE_ACCOUNT_ID: EmailStr = (
        "tasks@dummy-project.iam.gserviceaccount.com"
    )
    NOTIFICATION_TASKS_QUEUE_NAME: str = "send-notifications"
    SCHEDULE_ASSIGNMENTS_TASKS_QUEUE_NAME: str = "schedule-assignments"
    SCHEDULER_SERVICE_BASE_URL: HttpUrl = HttpUrl(
        "https://dummy-project-123.europe-west1.run.app/"
    )
    APPLICATION_SERVICE: Literal["back", "scheduler", "all"] = "back"
    USE_FIRESTORE_EMULATOR: bool = False
    USE_FIREBASE_AUTH_EMULATOR: bool = False
    USE_DIRECT_SCHEDULERS: bool = False

    TEST_NOTIFICATION_TITLE: str = "Test Notification from Language Track App"
    TEST_NOTIFICATION_MESSAGE: str = "This is a test notification."

    USE_GOOGLE_CLOUD_LOGGING: bool = False

    MAILGUN_API_KEY: Optional[str] = None
    MAILGUN_API_URL: Optional[str] = None
    MAILGUN_SENDER: Optional[str] = None

    VONAGE_API_KEY: Optional[str] = None
    VONAGE_API_SECRET: Optional[str] = None
    VONAGE_SENDER: Optional[str] = None

    model_config = SettingsConfigDict(env_file="settings/env.local-dev")


@dataclass
class AppConfiguration:

    @cached_property
    def user_repository(self) -> UserRepository:
        return FirestoreUserRepository(
            client=get_firestore_client(),
        )

    @cached_property
    def assignment_repository(self) -> AssignmentRepository:
        return FirestoreAssignmentRepository(
            client=get_firestore_client(),
            expiration_delay=timedelta(
                hours=get_settings().ASSIGNMENT_EXPIRATION_DELAY_HOURS
            ),
        )

    @cached_property
    def schedule_repository(self) -> ScheduleRepository:
        return FirestoreScheduleRepository(
            client=get_firestore_client(),
        )

    @cached_property
    def survey_repository(self) -> SurveyRepository:
        return FirestoreSurveyRepository(
            client=get_firestore_client(),
        )

    @cached_property
    def group_repository(self) -> GroupRepository:
        return FirestoreGroupRepository(
            client=get_firestore_client(),
        )

    @cached_property
    def assignment_limit_on_app_home_page(self) -> int:
        return get_settings().ASSIGNMENT_LIMIT_ON_APP_HOME_PAGE

    @cached_property
    def notification_service(self) -> NotificationService:
        return NotificationService(
            publishers=[
                self.mailgun_notification_publisher,
                self.vonage_notification_publisher,
                self.expo_notification_publisher,
            ],
            user_repository=self.user_repository,
            assignment_repository=self.assignment_repository,
            survey_repository=self.survey_repository,
        )

    @cached_property
    def mailgun_notification_publisher(self) -> MailgunNotificationPublisher:
        api_key = get_settings().MAILGUN_API_KEY
        api_url = get_settings().MAILGUN_API_URL
        sender = get_settings().MAILGUN_SENDER
        assert (
            api_key and api_url and sender
        ), "Missing Mailgun API key, API URL, or sender"

        api = MailgunAPI(
            api_key=api_key,
            api_url=api_url,
        )
        return MailgunNotificationPublisher(
            api=api,
            sender=sender,
        )

    @cached_property
    def vonage_notification_publisher(self) -> VonageNotificationPublisher:
        api_key = get_settings().VONAGE_API_KEY
        api_secret = get_settings().VONAGE_API_SECRET
        sender = get_settings().VONAGE_SENDER
        assert (
            api_key and api_secret and sender
        ), "Missing Vonage API key, API secret, or sender"

        client = vonage.Client(
            key=api_key,
            secret=api_secret,
        )
        return VonageNotificationPublisher(
            client=client,
            sender=sender,
        )

    @cached_property
    def expo_notification_publisher(self) -> ExpoNotificationPublisher:
        return ExpoNotificationPublisher(expo_api=ExpoAPI())

    @cached_property
    def cloud_tasks_notification_scheduler(self) -> NotificationScheduler:
        return CloudTasksNotificationScheduler(
            tasks_api=CloudTasksAPI(
                client=tasks_v2.CloudTasksClient(),
                url=HttpUrl(
                    urljoin(
                        str(get_settings().SCHEDULER_SERVICE_BASE_URL), "notify-user/"
                    )
                ),
                project_id=get_settings().PROJECT_NAME,
                location=get_settings().PROJECT_LOCATION,
                queue_name=get_settings().NOTIFICATION_TASKS_QUEUE_NAME,
                service_account_email=get_settings().CLOUD_TASKS_SERVICE_ACCOUNT_ID,
            ),
        )

    @cached_property
    def direct_notification_scheduler(self) -> NotificationScheduler:
        return DirectNotificationScheduler(
            user_repository=self.user_repository,
            notification_service=self.notification_service,
        )

    @cached_property
    def assignment_service(self) -> AssignmentService:
        if get_settings().USE_DIRECT_SCHEDULERS:
            notification_scheduler = self.direct_notification_scheduler
        else:
            notification_scheduler = self.cloud_tasks_notification_scheduler

        delays = get_settings().SOON_TO_EXPIRE_NOTIFICATION_DELAYS_MINUTES
        return AssignmentService(
            assignment_repository=self.assignment_repository,
            notification_scheduler=notification_scheduler,
            survey_repository=self.survey_repository,
            reminder_notification_delays=[timedelta(minutes=delay) for delay in delays],
        )

    @cached_property
    def cloud_tasks_assignment_scheduler(self) -> AssignmentScheduler:
        return CloudTasksAssignmentScheduler(
            tasks_api=CloudTasksAPI(
                client=tasks_v2.CloudTasksClient(),
                url=HttpUrl(
                    urljoin(
                        str(get_settings().SCHEDULER_SERVICE_BASE_URL),
                        "schedule-assignment/",
                    )
                ),
                project_id=get_settings().PROJECT_NAME,
                location=get_settings().PROJECT_LOCATION,
                queue_name=get_settings().SCHEDULE_ASSIGNMENTS_TASKS_QUEUE_NAME,
                service_account_email=get_settings().CLOUD_TASKS_SERVICE_ACCOUNT_ID,
            ),
        )

    @cached_property
    def direct_assignment_scheduler(self) -> AssignmentScheduler:
        return DirectAssignmentScheduler(
            assignment_service=self.assignment_service,
        )

    @cached_property
    def scheduler_service(self) -> SchedulerService:
        if get_settings().USE_DIRECT_SCHEDULERS:
            assignment_scheduler = self.direct_assignment_scheduler
        else:
            assignment_scheduler = self.cloud_tasks_assignment_scheduler
        return SchedulerService(
            assignment_scheduler=assignment_scheduler,
            schedule_repository=self.schedule_repository,
            group_repository=self.group_repository,
        )


__settings: Settings | None = None
__configuration: AppConfiguration | None = None


def get_configuration() -> AppConfiguration:
    global __configuration
    if __configuration is None:
        __configuration = AppConfiguration()
    return __configuration


class Environment(str, Enum):
    LOCAL_PROD = "local-prod"
    LOCAL_DEV = "local-dev"


def get_settings(local_env: Environment | None = None) -> Settings:
    global __settings
    if __settings is None:

        if local_env is not None:
            if local_env == Environment.LOCAL_PROD:
                file = "settings/env.local-prod"
            elif local_env == Environment.LOCAL_DEV:
                file = "settings/env.local-dev"
            else:
                raise ValueError(f"Invalid local_env: {local_env}")
            __settings = Settings(_env_file=file)  # type:ignore
        else:
            __settings = Settings()

    return __settings


def set_environment(local_env: Environment) -> None:
    get_settings(local_env)


@cache
def get_firestore_client(use_emulator: bool = False) -> google.cloud.firestore.Client:
    if (use_emulator or get_settings().USE_FIRESTORE_EMULATOR) and not os.environ.get(
        "FIRESTORE_EMULATOR_HOST"
    ):
        os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"
    get_firebase_app()
    return firebase_admin.firestore.client()


@cache
def get_firebase_app() -> firebase_admin.App:
    """
    Initialize Firebase App.

    If you want to use the Firestore and/or the Auth emulator, run:

        ./firebase-tools-linux --project dummy-project emulators:start --only firestore,auth
    """
    if get_settings().USE_FIREBASE_AUTH_EMULATOR:
        os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = "127.0.0.1:9099"

    return firebase_admin.initialize_app(
        options=dict(
            projectId=get_settings().PROJECT_NAME,
        )
    )


def get_project_name() -> str:
    return get_settings().PROJECT_NAME


def get_allowed_origins() -> list[str]:
    return get_settings().ALLOWED_ORIGINS


def get_scheduler_service() -> SchedulerService:
    return get_configuration().scheduler_service


def get_assignment_service() -> AssignmentService:
    return get_configuration().assignment_service


def get_notification_service() -> NotificationService:
    return get_configuration().notification_service


def get_application_service() -> Literal["back", "scheduler", "all"]:
    return get_settings().APPLICATION_SERVICE


def get_survey_repository() -> SurveyRepository:
    return get_configuration().survey_repository


def get_user_repository() -> UserRepository:
    return get_configuration().user_repository


def get_assignment_repository() -> AssignmentRepository:
    return get_configuration().assignment_repository


def get_schedule_repository() -> ScheduleRepository:
    return get_configuration().schedule_repository


def get_test_notification() -> NotificationMessage:
    return NotificationMessage(
        title=get_settings().TEST_NOTIFICATION_TITLE,
        message=get_settings().TEST_NOTIFICATION_MESSAGE,
    )


def get_use_google_cloud_logging() -> bool:
    return get_settings().USE_GOOGLE_CLOUD_LOGGING


def get_mailgun_notification_publisher() -> MailgunNotificationPublisher:
    return get_configuration().mailgun_notification_publisher


def get_vonage_notification_publisher() -> VonageNotificationPublisher:
    return get_configuration().vonage_notification_publisher


def get_expo_notification_publisher() -> ExpoNotificationPublisher:
    return get_configuration().expo_notification_publisher
