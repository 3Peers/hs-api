from datetime import timedelta
from django.shortcuts import reverse
from django.utils import timezone
from oauth2_provider.models import Application
from rest_framework.test import APITestCase
from ..models import User, SignUpOTP
from ..views import (
    BAD_CLIENT,
    INVALID_OTP,
    OTP_ATTEMPT_EXCEEDED,
    OTP_EXPIRED,
    OTP_SUCCESS,
    TEMPORARY_BLOCKED_EMAIL
)
from ..constants import OTP_MAX_ATTEMPTS
from globals.constants import ResponseMessages


class SendOTPAPITestCase(APITestCase):
    """
    APITestCase class to test `/user/send-otp/` endpoint.

    TODO: monitor celery worker to verify
          the send_mail task is queued.
          Can be kept optional and rely on
          task's unit tests.
    """
    CLIENT_ID = "boofar"

    def setUp(self):
        user = User.objects.create(username='oort', email='oort@oort.com')
        app = Application.objects.create(user=user, client_id=self.CLIENT_ID)
        self.url = reverse('send_otp_view')
        self.otp_obj = SignUpOTP.objects.create(
            email='a@b.cm',
            client=app,
            expires_at=timezone.now(),
            blocked_until=timezone.now() + timedelta(days=1)
        )

    def test_get_request(self):
        """Should not allow to request with GET at /user/signup/send-otp/
        """
        response = self.client.get(self.url, format='json')
        expected_status_code = 405
        self.assertEqual(response.status_code, expected_status_code)

    def test_bad_client(self):
        """Should be forbidden to access `/user/signup/send-otp/` with no client_id
        """
        data = {'client_id': 'foobar'}
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 403
        expected_resp_message = BAD_CLIENT
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_invalid_email(self):
        """Should be a bad request if `email` is not valid
        """
        data = {'client_id': self.CLIENT_ID, 'email': 'invalid'}
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 400
        expected_resp_message = ResponseMessages.INVALID_EMAIL
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_existing_email(self):
        """Should be forbidden for existing user to access `/user/signup/send-otp/`
        """
        data = {'client_id': self.CLIENT_ID, 'email': 'oort@oort.com'}
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 403
        self.assertEqual(response.status_code, expected_status_code)

    def test_new_otp(self):
        """Should be success if the request has valid `client_id` and `email`
        """
        data = {'client_id': self.CLIENT_ID, 'email': 'hs@hs.cm'}
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 200
        expected_resp_message = OTP_SUCCESS
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_blocked_email(self):
        """Should be forbidden for blocked email to access `/user/signup/send-otp/`
        """
        data = {'client_id': self.CLIENT_ID, 'email': self.otp_obj.email}
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 403
        expected_resp_message = TEMPORARY_BLOCKED_EMAIL
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_resend_expired_otp(self):
        """Should be success to resend expired otp
        """
        # unblock the email
        self.otp_obj.blocked_until = None
        self.otp_obj.save()

        data = {'client_id': self.CLIENT_ID, 'email': self.otp_obj.email}
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 200
        expected_resp_message = OTP_SUCCESS
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_resend_otp(self):
        """Should be success on resend and return with `email` which requested
        """
        self.otp_obj.blocked_until = None
        self.otp_obj.expires_at = timezone.now() + timedelta(days=1)
        self.otp_obj.save()

        data = {'client_id': self.CLIENT_ID, 'email': self.otp_obj.email}
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 200
        expected_resp_message = OTP_SUCCESS
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)


class VerifyOTPAPITestCase(APITestCase):
    """APITestCase class to test `/user/verify-otp/` endpoint.
    """
    CLIENT_ID = "boofar"

    def setUp(self):
        user = User.objects.create(username='oort', email='oort@oort.com')
        app = Application.objects.create(user=user, client_id=self.CLIENT_ID)
        self.url = reverse('verify_otp_view')
        self.expired_otp_obj = SignUpOTP.objects.create(
            email='a@b.cm',
            client=app,
            expires_at=timezone.now()
        )

        self.correct_otp_obj = SignUpOTP.create_otp_for_email('a@b.mc', app)

    def test_bad_client(self):
        """Should be forbidden to access `/user/signup/send-otp/` with bad `client_id`
        """
        data = {'client_id': 'foobar'}
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 403
        expected_resp_message = BAD_CLIENT
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_expired_otp(self):
        """Should be a bad request if expired token is provided
        """
        data = {'client_id': 'boofar', 'email': 'a@b.cm', 'otp': 'any otp'}
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 400
        expected_resp_message = OTP_EXPIRED
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_invalid_otp(self):
        """Should be a bad request if wrong otp is given
        """

        data = {'client_id': 'boofar', 'email': 'a@b.mc', 'otp': 'wrong otp'}
        response = self.client.post(self.url, format='json', data=data)

        expected_status_code = 400
        expected_resp_message = INVALID_OTP
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_otp_attempt_limit(self):
        """Should be a bad request if OTP attepts have been exceeded
        """

        data = {'client_id': 'boofar', 'email': 'a@b.mc', 'otp': 'wrong otp'}
        response = None
        for _ in range(OTP_MAX_ATTEMPTS + 1):
            response = self.client.post(self.url, format='json', data=data)

        expected_status_code = 400
        expected_resp_message = OTP_ATTEMPT_EXCEEDED
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_correct_otp_attempt(self):
        """Should be a success if OTP matches
        """

        data = {'client_id': 'boofar', 'email': 'a@b.mc', 'otp': self.correct_otp_obj.one_time_code}
        response = self.client.post(self.url, format='json', data=data)

        expected_status_code = 200
        self.assertEqual(response.status_code, expected_status_code)
        self.assertTrue({'access_token', 'refresh_token', 'expires'} < response.data.keys())

    def test_existing_user_email(self):
        """Should be forbidden for existing users to hit `/user/signup/verify-token/`
        """

        data = {'client_id': 'boofar', 'email': 'oort@oort.com', 'otp': 'random otp'}
        response = self.client.post(self.url, format='json', data=data)

        expected_status_code = 403
        self.assertEqual(response.status_code, expected_status_code)
