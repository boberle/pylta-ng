from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal, cast

import pydantic
from google.cloud import firestore

from lta.domain.group import Group
from lta.domain.group_repository import GroupNotFound, GroupRepository


class StoredGroup(Group):
    revision: Literal[1] = 1


@dataclass
class FirestoreGroupRepository(GroupRepository):
    client: firestore.Client
    collection_name: str = "groups"

    def list_groups(self) -> List[Group]:
        groups_ref = self.client.collection(self.collection_name)
        docs = groups_ref.stream()
        stored_groups = (
            pydantic.TypeAdapter(StoredGroup).validate_python(doc.to_dict())
            for doc in docs
        )
        return pydantic.TypeAdapter(list[Group]).validate_python(
            [g.model_dump() for g in stored_groups]
        )

    def get_group(self, id: str) -> Group:
        group_ref = self.client.collection(self.collection_name).document(id)
        doc = group_ref.get()
        if not doc.exists:
            raise GroupNotFound(group_id=id)
        stored_group = pydantic.TypeAdapter(StoredGroup).validate_python(doc.to_dict())
        return pydantic.TypeAdapter(Group).validate_python(stored_group.model_dump())

    def create_group(self, id: str, name: str, created_at: datetime) -> None:
        group_ref = self.client.collection(self.collection_name).document(id)
        if group_ref.get().exists:
            raise ValueError(f"Group with id {id} already exists.")
        group = StoredGroup(id=id, name=name, user_ids=[])
        group_ref.set(group.model_dump())

    def remove_group(self, id: str) -> None:
        group_ref = self.client.collection(self.collection_name).document(id)
        if not group_ref.get().exists:
            raise GroupNotFound(group_id=id)
        group_ref.delete()

    def exists(self, id: str) -> bool:
        group_ref = self.client.collection(self.collection_name).document(id)
        return cast(bool, group_ref.get().exists)

    def add_user_to_group(self, group_id: str, user_id: str) -> None:
        group_ref = self.client.collection(self.collection_name).document(group_id)
        doc = group_ref.get()
        if not doc.exists:
            raise GroupNotFound(group_id=group_id)

        group = pydantic.TypeAdapter(StoredGroup).validate_python(doc.to_dict())
        if user_id not in group.user_ids:
            group.user_ids.append(user_id)
            group_ref.set(group.model_dump())

    def remove_user_from_group(self, group_id: str, user_id: str) -> None:
        group_ref = self.client.collection(self.collection_name).document(group_id)
        doc = group_ref.get()
        if not doc.exists:
            raise GroupNotFound(group_id=group_id)

        group = pydantic.TypeAdapter(StoredGroup).validate_python(doc.to_dict())
        if user_id in group.user_ids:
            group.user_ids.remove(user_id)
            group_ref.set(group.model_dump())

    def set_users(self, group_id: str, user_ids: list[str]) -> None:
        group_ref = self.client.collection(self.collection_name).document(group_id)
        doc = group_ref.get()
        if not doc.exists:
            raise GroupNotFound(group_id=group_id)

        group = pydantic.TypeAdapter(StoredGroup).validate_python(doc.to_dict())
        group.user_ids = user_ids
        group_ref.set(group.model_dump())
