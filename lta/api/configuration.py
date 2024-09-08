import os
from dataclasses import dataclass
from datetime import timedelta
from functools import cache, cached_property

import firebase_admin
import firebase_admin.firestore
import google.cloud.firestore
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from lta.domain.assignment_repository import AssignmentRepository
from lta.domain.group_repository import GroupRepository
from lta.domain.schedule_repository import ScheduleRepository
from lta.domain.scheduler.assignment_service import AssignmentService
from lta.domain.scheduler.notification_service import NotificationService
from lta.domain.scheduler.scheduler_service import SchedulerService
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
from lta.infra.scheduler.assignment_scheduler import DirectAssignmentScheduler
from lta.infra.scheduler.notification_publisher import RecordingNotificationPublisher
from lta.infra.scheduler.notification_scheduler import DirectNotificationScheduler


class Settings(BaseSettings):
    PROJECT_NAME: str = "dummy-project"
    ALLOWED_ORIGINS: list[str] = Field(default_factory=list)
    ADMIN_EMAIL_ADDRESSES: list[str] = Field(default_factory=list)
    ASSIGNMENT_LIMIT_ON_APP_HOME_PAGE: int = 20

    model_config = SettingsConfigDict(env_file="settings/env.dev")


@dataclass
class AppConfiguration:

    @cached_property
    def firestore_client(self) -> google.cloud.firestore.Client:
        get_firebase_app()
        return firebase_admin.firestore.client()

    @cached_property
    def user_repository(self) -> UserRepository:
        return FirestoreUserRepository(
            client=self.firestore_client,
        )

    @cached_property
    def assignment_repository(self) -> AssignmentRepository:
        return FirestoreAssignmentRepository(
            client=self.firestore_client,
        )

    @cached_property
    def schedule_repository(self) -> ScheduleRepository:
        return FirestoreScheduleRepository(
            client=self.firestore_client,
        )

    @cached_property
    def survey_repository(self) -> SurveyRepository:
        return FirestoreSurveyRepository(
            client=self.firestore_client,
        )

    @cached_property
    def group_repository(self) -> GroupRepository:
        return FirestoreGroupRepository(
            client=self.firestore_client,
        )

    @cached_property
    def assignment_limit_on_app_home_page(self) -> int:
        return _settings.ASSIGNMENT_LIMIT_ON_APP_HOME_PAGE

    @cached_property
    def notification_service(self) -> NotificationService:
        return NotificationService(
            ios_notification_publisher=RecordingNotificationPublisher(),
            android_notification_publisher=RecordingNotificationPublisher(),
            user_repository=self.user_repository,
        )

    @cached_property
    def assignment_service(self) -> AssignmentService:
        return AssignmentService(
            assignment_repository=self.assignment_repository,
            notification_scheduler=DirectNotificationScheduler(
                user_repository=self.user_repository,
                notification_service=self.notification_service,
            ),
            survey_repository=self.survey_repository,
            soon_to_expire_notification_delay=timedelta(minutes=30),
        )

    @cached_property
    def scheduler_service(self) -> SchedulerService:
        return SchedulerService(
            assignment_scheduler=DirectAssignmentScheduler(
                assignment_service=self.assignment_service,
            ),
            schedule_repository=self.schedule_repository,
            group_repository=self.group_repository,
        )


_settings = Settings()
_configuration = AppConfiguration()


def get_configuration() -> AppConfiguration:
    return _configuration


@cache
def get_firestore_client(use_emulator: bool = False) -> google.cloud.firestore.Client:
    if use_emulator and not os.environ.get("FIRESTORE_EMULATOR_HOST"):
        os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"
    get_firebase_app()
    return _configuration.firestore_client


@cache
def get_firebase_app() -> firebase_admin.App:
    """
    Initialize Firebase App.

    If you want to use the Firestore emulator, run:

        ./firebase-tools-linux --project dummy-project emulators:start --only firestore
    """
    return firebase_admin.initialize_app(
        options=dict(
            projectId=_settings.PROJECT_NAME,
        )
    )


def get_project_name() -> str:
    return _settings.PROJECT_NAME


def get_allowed_origins() -> list[str]:
    return _settings.ALLOWED_ORIGINS


def get_admin_email_addresses() -> list[str]:
    return _settings.ADMIN_EMAIL_ADDRESSES


def get_scheduler_service() -> SchedulerService:
    return _configuration.scheduler_service


def get_assignment_service() -> AssignmentService:
    return _configuration.assignment_service


def get_notification_service() -> NotificationService:
    return _configuration.notification_service
