from django.test import TestCase, RequestFactory
from django.utils import timezone
from unittest.mock import patch
from waitlist.models import Waitlist
from waitlist.views import VerifyWaitlistView
import uuid


class VerifyWaitlistViewUnitTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = VerifyWaitlistView.as_view()
        self.token = uuid.uuid4()

        self.waitlist = Waitlist.objects.create(
            email="user@example.com",
            username="funmi",
            token=self.token,
            is_verified=False,
        )

    def test_verify_waitlist_success(self):
        request = self.factory.get(f"/api/waitlist/verify/?token={self.token}")
        response = self.view(request)

        self.assertEqual(response.status_code, 200)

        self.waitlist.refresh_from_db()
        self.assertTrue(self.waitlist.is_verified)

    def test_verify_waitlist_invalid_token(self):
        invalid_token = uuid.uuid4()
        request = self.factory.get(f"/api/waitlist/verify/?token={invalid_token}")
        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid or expired token", response.data["message"])

    def test_missing_token(self):
        request = self.factory.get("/api/waitlist/verify/")
        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn("token is required", str(response.data).lower())

    @patch("waitlist.views.logger")
    def test_internal_error_logged(self, mock_logger):
        with patch("waitlist.views.Waitlist.objects.get") as mock_get:
            mock_get.side_effect = Exception("DB error")

            request = self.factory.get(f"/api/waitlist/verify/?token={self.token}")
            response = self.view(request)

            self.assertEqual(response.status_code, 500)
            mock_logger.error.assert_called()
