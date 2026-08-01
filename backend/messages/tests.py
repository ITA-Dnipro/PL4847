from django.contrib.auth import get_user_model
from django.test import TestCase
from projects.models import Project
from startups.models import StartupProfile

from .models import Message, Notification

User = get_user_model()


class MessageNotificationTests(TestCase):
    def setUp(self):
        self.startup_user = User.objects.create_user(
            username="startup-message-user",
            email="startup-message@example.com",
            password="test-password",
            role=User.Role.STARTUP,
        )

        self.investor_user = User.objects.create_user(
            username="investor-message-user",
            email="investor-message@example.com",
            password="test-password",
            role=User.Role.INVESTOR,
        )

        self.startup = StartupProfile.objects.create(
            user=self.startup_user,
            company_name="Message Test Startup",
            slug="message-test-startup",
        )

        self.project = Project.objects.create(
            startup=self.startup,
            title="Message Test Project",
            slug="message-test-project",
        )

    def test_message_creation(self):
        message = Message.objects.create(
            sender=self.investor_user,
            recipient=self.startup_user,
            project=self.project,
            body="Hello, I am interested in your project.",
        )

        self.assertEqual(message.sender, self.investor_user)
        self.assertEqual(message.recipient, self.startup_user)
        self.assertEqual(message.project, self.project)
        self.assertEqual(
            message.body,
            "Hello, I am interested in your project.",
        )

    def test_message_can_exist_without_project(self):
        message = Message.objects.create(
            sender=self.investor_user,
            recipient=self.startup_user,
            body="Hello.",
        )

        self.assertIsNone(message.project)

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.startup_user,
            message="An investor contacted you.",
        )

        self.assertEqual(notification.user, self.startup_user)
        self.assertEqual(
            notification.message,
            "An investor contacted you.",
        )

    def test_notification_is_unread_by_default(self):
        notification = Notification.objects.create(
            user=self.startup_user,
            message="New notification.",
        )

        self.assertFalse(notification.is_read)
