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
        """
        Should return HTTP status code 405
        when the user makes a GET HTTP request
        """
        response = self.client.get(self.url, format='json')
        expected_status_code = 405
        self.assertEqual(response.status_code, expected_status_code)

    def test_bad_client(self):
        """
        Should return HTTP status code `403`
        when there is no `Application` for the `client_id`
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
        """
        Should return HTTP status code 400
        when the `email` is invalid
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
        """
        Should return HTTP status code 403
        when a user already exists with the `email`
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
        """
        Should return HTTP status code 200
        with a mail when a new otp is created.
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
        """
        Should return HTTP status code 403
        when the email has been blocked
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
        """
        Should return HTTP status code 200
        with a mail when a otp is requested which has expired
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
        """
        Should return HTTP status code 200
        with a mail when a otp is requested to be resent
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
    """
    APITestCase class to test `/user/verify-otp/` endpoint.

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
        """
        Should return HTTP status code `403`
        when there is no `Application` for the `client_id`
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
        """
        Should return HTTP status code `400`
        when user enters expired otp
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
        """
        Should return HTTP status code `400`
        when wrong otp is entered
        """

        data = {'client_id': 'boofar', 'email': 'a@b.mc', 'otp': 'wrong otp'}
        response = self.client.post(self.url, format='json', data=data)

        expected_status_code = 400
        expected_resp_message = INVALID_OTP
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_otp_attempt_limit(self):
        """
        Should return HTTP status code `400`
        when OTP Attempts limit exceed
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
        """
        Should return HTTP status code `200`
        when OTP matches
        """

        data = {'client_id': 'boofar', 'email': 'a@b.mc', 'otp': self.correct_otp_obj.one_time_code}
        response = self.client.post(self.url, format='json', data=data)

        expected_status_code = 200
        self.assertEqual(response.status_code, expected_status_code)
        self.assertTrue({'access_token', 'refresh_token', 'expires'} < response.data.keys())

    def test_existing_user_email(self):
        """
        Should return HTTP status code `403`
        when user with provided email already exists
        """

        data = {'client_id': 'boofar', 'email': 'oort@oort.com', 'otp': 'random otp'}
        response = self.client.post(self.url, format='json', data=data)

        expected_status_code = 403
        self.assertEqual(response.status_code, expected_status_code)
