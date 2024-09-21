from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal, cast

import pydantic
from google.cloud import firestore
from pydantic import EmailStr

from lta.domain.user import Device, DeviceOS, User
from lta.domain.user_repository import UserNotFound, UserRepository


class StoredUser(User):
    revision: Literal[1] = 1


@dataclass
class FirestoreUserRepository(UserRepository):
    client: firestore.Client
    collection_name: str = "users"

    def list_users(self) -> List[User]:
        users_ref = self.client.collection(self.collection_name)
        docs = users_ref.stream()
        stored_users = (
            pydantic.TypeAdapter(StoredUser).validate_python(doc.to_dict())
            for doc in docs
        )
        return pydantic.TypeAdapter(list[User]).validate_python(
            [u.model_dump() for u in stored_users]
        )

    def get_device_registrations_from_user_id(self, id: str) -> List[Device]:
        user = self.get_user(id)
        return user.devices

    def get_user(self, id: str) -> User:
        user_ref = self.client.collection(self.collection_name).document(id)
        doc = user_ref.get()
        if not doc.exists:
            raise UserNotFound(user_id=id)
        stored_user = pydantic.TypeAdapter(StoredUser).validate_python(doc.to_dict())
        return pydantic.TypeAdapter(User).validate_python(stored_user.model_dump())

    def add_device_registration(
        self, id: str, token: str, os: DeviceOS, version: str | None, date: datetime
    ) -> None:
        user = self.get_user(id)

        for device in user.devices:
            if device.token == token:
                device.add_connection_time(date)
                break
        else:
            user.devices.append(
                Device(
                    token=token,
                    os=os,
                    version=version,
                    first_connection=date,
                    last_connection=date,
                )
            )

        self.client.collection(self.collection_name).document(id).update(
            {"devices": [d.model_dump() for d in user.devices]}
        )

    def create_user(
        self, id: str, email_address: EmailStr, created_at: datetime
    ) -> None:
        user = StoredUser(
            id=id,
            email_address=email_address,
            created_at=created_at,
            devices=[],
        )
        self.client.collection(self.collection_name).document(id).set(user.model_dump())

    def exists(self, id: str) -> bool:
        user_ref = self.client.collection(self.collection_name).document(id)
        return cast(bool, user_ref.get().exists)
