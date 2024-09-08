import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
from pydantic import EmailStr, HttpUrl


@dataclass
class CloudTasksAPI:
    client: tasks_v2.CloudTasksClient
    url: HttpUrl
    project_id: str
    location: str
    queue_name: str
    service_account_email: EmailStr

    def create_task(
        self,
        payload: dict[Any, Any],
        task_id: str | None = None,
        when: datetime | None = None,
    ) -> None:
        task = tasks_v2.Task(
            http_request=tasks_v2.HttpRequest(
                http_method=tasks_v2.HttpMethod.POST,
                url=str(self.url),
                headers={"Content-type": "application/json"},
                body=json.dumps(payload).encode(),
                oidc_token=tasks_v2.OidcToken(
                    service_account_email=str(self.service_account_email),
                    audience=str(self.url),
                ),
            ),
            name=(
                self.client.task_path(
                    self.project_id, self.location, self.queue_name, task_id
                )
                if task_id is not None
                else None
            ),
        )

        if when is not None:
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(when)
            task.schedule_time = timestamp

        self.client.create_task(
            tasks_v2.CreateTaskRequest(
                parent=self.client.queue_path(
                    self.project_id, self.location, self.queue_name
                ),
                task=task,
            )
        )

    @staticmethod
    def generate_task_id(*args: Any) -> str:
        chunks = []
        for arg in args:
            if isinstance(arg, str):
                chunks.append(re.sub(r"[^-_a-zA-Z0-9]", "-", arg))
            elif isinstance(arg, int):
                chunks.append(str(arg))
            elif isinstance(arg, datetime):
                chunks.append(arg.strftime("%Y%m%d-%H%M%S"))
            elif isinstance(arg, float):
                chunks.append(str(arg).replace(".", "-"))
            else:
                raise ValueError(f"Unsupported argument type: {type(arg)}")
        return "-".join(chunks)
