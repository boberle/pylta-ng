from dataclasses import dataclass
from functools import cached_property

from lta.domain.user_repository import UserRepository
from lta.infra.repositories.memory.user_repository import InMemoryUserRepository


@dataclass
class AppConfiguration:

    @cached_property
    def user_repository(self) -> UserRepository:
        return InMemoryUserRepository()


_configuration = AppConfiguration()


def get_configuration() -> AppConfiguration:
    return _configuration
