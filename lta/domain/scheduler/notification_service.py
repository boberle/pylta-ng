import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from lta.domain.assignment import Assignment
from lta.domain.assignment_repository import AssignmentRepository
from lta.domain.scheduler.notification_pulisher import (
    NotificationPublisher,
    NotificationType,
)
from lta.domain.survey_repository import SurveyRepository
from lta.domain.user import User
from lta.domain.user_repository import UserRepository


@dataclass
class NotificationService:
    """
    The notification service is used to send a notification message to a user.

    It requires a user id and an assignment id.

    The notification channel is determined by the available information
    - on the user: phone number (SMS), email address (email), or device token (push notification)
    - on the survey (found in the assignment): notification title and message for each channel

    The service also update the assignment with the notification time.

    The notification is sent only if the assignment is not already submitted.
    """

    publishers: list[NotificationPublisher]
    user_repository: UserRepository
    assignment_repository: AssignmentRepository
    survey_repository: SurveyRepository

    def notify_user(
        self,
        user_id: str,
        assignment_id: str,
        notification_type: NotificationType,
        when: datetime | None = None,
    ) -> None:
        """
        Send a notification now.

        `when` is the time to be written in the assignment. It defaults to now if not provided.
        """
        user = self.user_repository.get_user(user_id)
        assignment = self.assignment_repository.get_assignment(user_id, assignment_id)
        if assignment.submitted_at is not None:
            logging.info(
                "Notification not sent: assignment is already submitted",
                extra=dict(
                    json_fields={"user_id": user_id, "assignment_id": assignment_id}
                ),
            )
            return

        has_sent = self.send_notification(user, assignment, notification_type)
        if not has_sent:
            logging.warning(
                "Notification not sent: no notification channel available",
                extra=dict(
                    json_fields={"user_id": user_id, "assignment_id": assignment_id}
                ),
            )
            return

        if when is None:
            when = datetime.now(tz=timezone.utc)
        self._update_assignment(user, assignment, when)

    def send_notification(
        self,
        user: User,
        assignment: Assignment,
        notification_type: NotificationType,
    ) -> bool:
        user_notification_info = user.notification_info
        if user_notification_info is None:
            return False

        survey = self.survey_repository.get_survey(assignment.survey_id)
        survey_notification_info = survey.notifications
        if survey_notification_info is None:
            return False

        sent = False
        for publisher in self.publishers:
            success = publisher.send_notification(
                user_id=user.id,
                assignment_id=assignment.id,
                user_notification_info=user_notification_info,
                survey_notification_info=survey_notification_info,
                notification_type=notification_type,
            )
            sent = sent or success
        return sent

    def _update_assignment(
        self, user: User, assignment: Assignment, when: datetime
    ) -> None:
        self.assignment_repository.notify_user(user.id, assignment.id, when=when)
