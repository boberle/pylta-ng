from typing import Any, cast

from google.cloud import firestore
from google.cloud.firestore_v1 import FieldFilter


def make_filter(field_path: Any, op_string: Any, value: Any) -> FieldFilter:
    """
    This function is a wrapper around the FieldFilter class from google-cloud-firestore.

    Don't use FieldFilter directly, because mypy will complain about using an untype function in a typed environment.
    """
    # TODO cast
    return FieldFilter(field_path=field_path, op_string=op_string, value=value)  # type: ignore


def get_collection_count(
    collection: firestore.CollectionReference | firestore.Query,
) -> int:
    return cast(int, collection.count().get()[0][0].value)
