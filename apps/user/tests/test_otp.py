from datetime import timedelta
from django.shortcuts import reverse
from django.utils import timezone
from model_mommy import mommy
from rest_framework.test import APITestCase
from ..models import SignUpOTP
from ..views import (
    BAD_CLIENT,
    INVALID_OTP,
    OTP_ATTEMPT_EXCEEDED,
    OTP_RESENDS_EXCEEDED,
    OTP_EXPIRED,
    OTP_SUCCESS,
    TEMPORARY_BLOCKED_EMAIL
)
from ..constants import OTP_MAX_ATTEMPTS, OTP_MAX_RESENDS
from apps.globals.constants import ResponseMessages


class SendOTPAPITestCase(APITestCase):
    """
    APITestCase class to test `/user/send-otp/` endpoint.

    TODO: monitor celery worker to verify
          the send_mail task is queued.
          Can be kept optional and rely on
          task's unit tests.
    """

    def setUp(self):
        model_name = 'SignUpOTP'
        now = timezone.now()
        tomorrow = now + timedelta(days=1)

        self.url = reverse('send_otp_view')
        self.blocked_otp_obj = mommy.make(
            model_name,
            expires_at=tomorrow,
            attempts_used=OTP_MAX_ATTEMPTS,
            blocked_until=tomorrow
        )
        self.expired_otp_obj = mommy.make(
            model_name,
            expires_at=now
        )
        self.resend_blocked_otp_obj = mommy.make(
            model_name,
            expires_at=tomorrow,
            resends_used=OTP_MAX_RESENDS
        )
        self.almost_resend_blocked_otp_obj = mommy.make(
            model_name,
            expires_at=tomorrow,
            resends_used=OTP_MAX_RESENDS - 1
        )
        self.valid_otp_obj = mommy.make(
            model_name,
            expires_at=tomorrow
        )
        self.client_id = self.valid_otp_obj.client.client_id
        self.existing_user = mommy.make('user.User', email='existing@user.com')

    def test_get_request(self):
        """Should not allow to request with GET at /user/signup/send-otp/
        """
        response = self.client.get(self.url)
        expected_status_code = 405
        self.assertEqual(response.status_code, expected_status_code)

    def test_bad_client(self):
        """Should be forbidden to access `/user/signup/send-otp/`
        with no client_id"""
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
        data = {'client_id': self.client_id, 'email': 'invalid'}
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
        """Should be forbidden for existing user to access
        `/user/signup/send-otp/`"""
        data = {'client_id': self.client_id, 'email': self.existing_user.email}
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
        data = {'client_id': self.client_id, 'email': 'hs@hs.cm'}
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
        """Should be forbidden for blocked email to access
        `/user/signup/send-otp/`"""
        data = {
            'client_id': self.blocked_otp_obj.client.client_id,
            'email': self.blocked_otp_obj.email
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 403
        expected_resp_message = TEMPORARY_BLOCKED_EMAIL
        self.assertEqual(self.blocked_otp_obj.attempts_used, OTP_MAX_ATTEMPTS)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_resend_blocked(self):
        """Should be forbidden for resend blocked email to access
        `/user/signup/send-otp/`"""
        data = {
            'client_id': self.resend_blocked_otp_obj.client.client_id,
            'email': self.resend_blocked_otp_obj.email
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 403
        expected_resp_message = OTP_RESENDS_EXCEEDED
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_expired_otp(self):
        """Should be success to resend expired otp
        """
        data = {
            'client_id': self.expired_otp_obj.client.client_id,
            'email': self.expired_otp_obj.email
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 200
        expected_resp_message = OTP_SUCCESS

        obj = SignUpOTP.objects.get(email=self.expired_otp_obj.email)
        self.assertEqual(obj.resends_used, 1)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_last_successful_resend(self):
        """Should be success with message resend exceeded
        on the last resend request"""
        data = {
            'client_id': self.almost_resend_blocked_otp_obj.client.client_id,
            'email': self.almost_resend_blocked_otp_obj.email
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 200
        expected_resp_message = OTP_RESENDS_EXCEEDED

        obj = SignUpOTP.objects.get(
            email=self.almost_resend_blocked_otp_obj.email)
        self.assertEqual(obj.resends_used, OTP_MAX_RESENDS)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_resend_otp(self):
        """Should be success on resend and return with `email` which requested
        """
        num_resends = self.valid_otp_obj.resends_used
        data = {
            'client_id': self.client_id,
            'email': self.valid_otp_obj.email
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 200
        expected_resp_message = OTP_SUCCESS

        obj = SignUpOTP.objects.get(email=self.valid_otp_obj.email)
        self.assertEqual(obj.resends_used, num_resends + 1)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)


class VerifyOTPAPITestCase(APITestCase):
    """APITestCase class to test `/user/verify-otp/` endpoint.
    """

    def setUp(self):
        model_name = 'SignUpOTP'
        now = timezone.now()
        tomorrow = timezone.now() + timedelta(days=1)

        self.existing_user = mommy.make('user.User', email='existing@user.com')
        self.url = reverse('verify_otp_view')
        self.expired_otp_obj = mommy.make(
            model_name,
            expires_at=now
        )
        self.max_attempts_otp_obj = mommy.make(
            model_name,
            expires_at=tomorrow
        )
        self.blocked_otp_obj = mommy.make(
            model_name,
            expires_at=tomorrow,
            attempts_used=OTP_MAX_ATTEMPTS,
            blocked_until=tomorrow
        )
        self.valid_otp_obj = mommy.make(
            model_name,
            expires_at=tomorrow
        )
        self.client_id = self.valid_otp_obj.client.client_id

    def test_get_request(self):
        """Should not allow to request with GET at /user/signup/send-otp/
        """
        response = self.client.get(self.url)
        expected_status_code = 405
        self.assertEqual(response.status_code, expected_status_code)

    def test_invalid_email(self):
        """Should be forbidden for existing users to hit
        `/user/signup/verify-token/`
        """

        data = {
            'client_id': 'boofar',
            'email': 'oort@oort.com',
            'otp': 'random otp'
        }
        response = self.client.post(self.url, data=data)

        expected_status_code = 403
        self.assertEqual(response.status_code, expected_status_code)

    def test_bad_client(self):
        """Should be forbidden to access `/user/signup/send-otp/`
        with bad `client_id`"""
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

    def test_no_otp(self):
        """Should be a bad request when there is no otp associated with
        email and client"""
        data = {'client_id': self.client_id, 'email': 'aaa@aaa.com'}
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 400
        expected_resp_message = ResponseMessages.BAD_REQUEST
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_blocked_email(self):
        """Should be forbidden for blocked email to access
        `/user/signup/send-otp/`"""
        data = {
            'client_id': self.blocked_otp_obj.client.client_id,
            'email': self.blocked_otp_obj.email
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 403
        expected_resp_message = TEMPORARY_BLOCKED_EMAIL
        self.assertEqual(self.blocked_otp_obj.attempts_used, OTP_MAX_ATTEMPTS)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_expired_otp(self):
        """Should be a bad request if expired token is provided
        """
        data = {
            'client_id': self.expired_otp_obj.client.client_id,
            'email': self.expired_otp_obj.email,
            'otp': 'any otp'
        }
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
        attempts_used = self.valid_otp_obj.attempts_used
        data = {
            'client_id': self.valid_otp_obj.client.client_id,
            'email': self.valid_otp_obj.email,
            'otp': 'wrong otp'
        }
        response = self.client.post(self.url, data=data)

        expected_status_code = 400
        expected_resp_message = INVALID_OTP

        obj = SignUpOTP.objects.get(email=self.valid_otp_obj.email)
        self.assertEqual(obj.attempts_used, attempts_used + 1)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_otp_attempt_limit(self):
        """Should be a bad request if OTP attempts have been exceeded
        """

        data = {
            'client_id': self.max_attempts_otp_obj.client.client_id,
            'email': self.max_attempts_otp_obj.email,
            'otp': 'wrong otp'
        }
        response = None
        for _ in range(OTP_MAX_ATTEMPTS):
            response = self.client.post(self.url, data=data)

        expected_status_code = 400
        expected_resp_message = OTP_ATTEMPT_EXCEEDED

        obj = SignUpOTP.objects.get(email=self.max_attempts_otp_obj.email)
        self.assertEqual(obj.attempts_used, OTP_MAX_ATTEMPTS)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_correct_otp_attempt(self):
        """Should be a success if OTP matches
        """

        data = {
            'client_id': self.valid_otp_obj.client.client_id,
            'email': self.valid_otp_obj.email,
            'otp': self.valid_otp_obj.one_time_code
        }
        response = self.client.post(self.url, data=data)

        expected_status_code = 200
        self.assertTrue(not SignUpOTP.objects.filter(
            email=self.valid_otp_obj.email
        ).exists())
        self.assertEqual(response.status_code, expected_status_code)
        self.assertTrue({
            'access_token',
            'refresh_token',
            'expires'
        } < response.data.keys())
