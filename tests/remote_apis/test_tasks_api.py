from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock

import pytest
from google.cloud import tasks_v2
from pydantic import HttpUrl

from lta.infra.tasks_api import CloudTasksAPI


@pytest.mark.parametrize(
    "args,exp",
    [
        (["test_string"], "test_string"),
        (["test string with spaces"], "test-string-with-spaces"),
        (["special@chars!"], "special-chars-"),
        (["string", 123], "string-123"),
        (["string", 123, 45.67], "string-123-45-67"),
        (["string", datetime(2023, 1, 1, 12, 0, 0)], "string-20230101-120000"),
        (
            ["string", 123, datetime(2023, 1, 1, 12, 0, 0), 45.67],
            "string-123-20230101-120000-45-67",
        ),
    ],
)
def test_generate_task_id(args: list[Any], exp: str) -> None:
    assert CloudTasksAPI.generate_task_id(*args) == exp


@pytest.mark.parametrize(
    "args",
    [
        ([None]),
        ([{"key": "value"}]),
    ],
)
def test_generate_task_id_invalid_args(args: list[Any]) -> None:
    with pytest.raises(ValueError):
        CloudTasksAPI.generate_task_id(*args)


@pytest.mark.parametrize(
    "url,exp",
    [
        (
            "https://example.com/page?param1=value1&param2=value2",
            "https://example.com/page",
        ),
        ("https://example.com/page", "https://example.com/page"),
        ("https://example.com/page#section", "https://example.com/page"),
        (
            "https://example.com/page/subpage?param=value",
            "https://example.com/page/subpage",
        ),
        ("https://example.com/?param=value", "https://example.com/"),
        ("https://example.com?param=value", "https://example.com"),
    ],
)
def test_remove_query_params(url: str, exp: str) -> None:
    assert CloudTasksAPI.remove_query_params(url) == exp


@pytest.fixture
def cloud_tasks_api() -> CloudTasksAPI:
    client = MagicMock(spec=tasks_v2.CloudTasksClient)
    client.task_path.side_effect = tasks_v2.CloudTasksClient.task_path
    client.queue_path.side_effect = tasks_v2.CloudTasksClient.queue_path
    url = HttpUrl("https://example.com/task-handler")
    project_id = "dummy-project"
    location = "us-central1"
    queue_name = "dummy-queue"
    service_account_email = "dummy@example.com"
    return CloudTasksAPI(
        client=client,
        url=url,
        project_id=project_id,
        location=location,
        queue_name=queue_name,
        service_account_email=service_account_email,
    )


def test_create_task(cloud_tasks_api: CloudTasksAPI) -> None:
    payload = {"key": "value"}
    task_id = "test-task-id"
    when = datetime(2023, 1, 2, 3, 4, 5)

    cloud_tasks_api.create_task(payload, task_id, when)

    cloud_tasks_api.client.create_task.assert_called_once()  # type:ignore
    args, _ = cloud_tasks_api.client.create_task.call_args  # type:ignore
    create_task_request = args[0]

    assert (
        create_task_request.parent
        == "projects/dummy-project/locations/us-central1/queues/dummy-queue"
    )
    assert (
        create_task_request.task.http_request.url == "https://example.com/task-handler"
    )
    assert create_task_request.task.http_request.body == b'{"key": "value"}'
    assert (
        create_task_request.task.http_request.headers["Content-type"]
        == "application/json"
    )
    assert (
        create_task_request.task.http_request.oidc_token.service_account_email
        == "dummy@example.com"
    )
    assert (
        create_task_request.task.http_request.oidc_token.audience
        == "https://example.com/task-handler"
    )
    assert (
        create_task_request.task.name
        == "projects/dummy-project/locations/us-central1/queues/dummy-queue/tasks/test-task-id"
    )
    assert create_task_request.task.schedule_time == datetime(
        2023, 1, 2, 3, 4, 5, tzinfo=timezone.utc
    )


def test_create_task_without_task_id(cloud_tasks_api: CloudTasksAPI) -> None:
    payload = {"key": "value"}
    cloud_tasks_api.create_task(payload)

    cloud_tasks_api.client.create_task.assert_called_once()  # type:ignore
    args, _ = cloud_tasks_api.client.create_task.call_args  # type:ignore
    create_task_request = args[0]
    assert create_task_request.task.name == ""


def test_create_task_without_when(cloud_tasks_api: CloudTasksAPI) -> None:
    payload = {"key": "value"}
    cloud_tasks_api.create_task(payload)

    cloud_tasks_api.client.create_task.assert_called_once()  # type:ignore
    args, _ = cloud_tasks_api.client.create_task.call_args  # type:ignore
    create_task_request = args[0]
    assert create_task_request.task.schedule_time is None
