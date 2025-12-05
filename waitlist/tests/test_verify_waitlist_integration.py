from rest_framework.test import APITestCase
from django.urls import reverse
from waitlist.models import Waitlist
import uuid


class VerifyWaitlistIntegrationTest(APITestCase):

    def setUp(self):
        self.token = uuid.uuid4()

        self.waitlist = Waitlist.objects.create(
            email="verify@example.com",
            username="tester",
            token=self.token,
            is_verified=False,
        )

        self.url = reverse("verify-waitlist")  # name in urls.py

    def test_verify_success_flow(self):
        """Full verification flow: DB → View → DB"""
        response = self.client.get(f"{self.url}?token={self.token}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Verification successful")

        self.waitlist.refresh_from_db()
        self.assertTrue(self.waitlist.is_verified)

    def test_verify_invalid_token(self):
        invalid = uuid.uuid4()

        response = self.client.get(f"{self.url}?token={invalid}")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["status"], "error")

    def test_verify_already_verified(self):
        """Should return graceful message if user already verified"""
        self.waitlist.is_verified = True
        self.waitlist.save()

        response = self.client.get(f"{self.url}?token={self.token}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("already verified", response.data["message"].lower())

    def test_missing_token(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("token", response.data["message"].lower())
