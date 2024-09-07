import os
from dataclasses import dataclass
from functools import cache, cached_property

import firebase_admin
import firebase_admin.firestore
import google.cloud.firestore
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from lta.domain.assignment_repository import AssignmentRepository
from lta.domain.survey_repository import SurveyRepository
from lta.domain.user_repository import UserRepository
from lta.infra.repositories.firestore.assignment_repository import (
    FirestoreAssignmentRepository,
)
from lta.infra.repositories.firestore.survey_repository import FirestoreSurveyRepository
from lta.infra.repositories.firestore.user_repository import FirestoreUserRepository


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
    def survey_repository(self) -> SurveyRepository:
        return FirestoreSurveyRepository(
            client=self.firestore_client,
        )

    @cached_property
    def assignment_limit_on_app_home_page(self) -> int:
        return _settings.ASSIGNMENT_LIMIT_ON_APP_HOME_PAGE


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
