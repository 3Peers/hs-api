from datetime import timedelta
from django.shortcuts import reverse
from django.utils import timezone
from oauth2_provider.models import Application
from rest_framework.test import APITestCase
from ..models import User, AuthOTP
from ..constants import ResponseMessages as UserResponseMessage
from ..constants import OTP_MAX_ATTEMPTS, OTP_MAX_RESENDS
from ..serializers import OTPVerificationContexts
from apps.globals.constants import ResponseMessages


class SignUpSendOTPAPITestCase(APITestCase):
    """
    APITestCase class to test `/user/signup/` endpoint.

    TODO: monitor celery worker to verify
          the send_mail task is queued.
          Can be kept optional and rely on
          task's unit tests.
    """
    CLIENT_ID = "boofar"

    def setUp(self):
        user = User.objects.create(username='oort', email='oort@oort.com')
        app = Application.objects.create(user=user, client_id=self.CLIENT_ID)
        self.url = reverse('sign_up_view')
        self.blocked_otp_obj = AuthOTP.objects.create(
            email='blocked@b.cm',
            client=app,
            expires_at=timezone.now() + timedelta(days=1),
            attempts_used=OTP_MAX_ATTEMPTS,
            blocked_until=timezone.now() + timedelta(days=1)
        )
        self.expired_otp_obj = AuthOTP.objects.create(
            email='expired@b.cm',
            client=app,
            expires_at=timezone.now()
        )
        self.resend_blocked_otp_obj = AuthOTP.objects.create(
            email='resend_blocked@b.cm',
            client=app,
            expires_at=timezone.now() + timedelta(days=1),
            resends_used=OTP_MAX_RESENDS
        )
        self.almost_resend_blocked_otp_obj = AuthOTP.objects.create(
            email='almost_resend_blocked@b.cm',
            client=app,
            expires_at=timezone.now() + timedelta(days=1),
            resends_used=OTP_MAX_RESENDS - 1
        )
        self.valid_otp_obj = AuthOTP.objects.create(
            email='valid@b.cm',
            client=app,
            expires_at=timezone.now() + timedelta(days=1)
        )

    def test_get_request(self):
        """Should not allow to request with GET at /user/sign-up/
        """
        response = self.client.get(self.url, format='json')
        expected_status_code = 405
        self.assertEqual(response.status_code, expected_status_code)

    def test_bad_client(self):
        """Should be a bad request with no client_id: `/user/sign-up/`
        """
        data = {
            'client_id': 'foobar',
            'email': 'random@r.cm',
            'password': 'random password'
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 400
        expected_resp_message = UserResponseMessage.BAD_CLIENT
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('client_id')[0], expected_resp_message)

    def test_invalid_email(self):
        """Should be a bad request if `email` is not valid: `/user/sign-up/`
        """
        data = {
            'client_id': self.CLIENT_ID,
            'email': 'invalid',
            'password': 'random password'
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 400
        self.assertEqual(response.status_code, expected_status_code)
        self.assertTrue('email' in response.data.keys())

    def test_existing_email(self):
        """Should be a bad request for existing user to access: `/user/sign-up/`
        """
        data = {
            'client_id': self.CLIENT_ID,
            'email': 'oort@oort.com',
            'password': 'random password'
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 400
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('email')[0], UserResponseMessage.USER_WITH_EMAIL_EXISTS)

    def test_new_otp(self):
        """Should be success if the request has valid data
        """
        data = {
            'client_id': self.CLIENT_ID,
            'email': 'hs@hs.cm',
            'password': 'random password'
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 200
        expected_resp_message = UserResponseMessage.OTP_SUCCESS

        user = User.objects.get(email=data.get('email'))

        self.assertFalse(user.is_active)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_blocked_email(self):
        """Should be bad request for blocked email to access: \
`/user/signup/send-otp/`"""
        data = {
            'client_id': self.CLIENT_ID,
            'email': self.blocked_otp_obj.email,
            'password': 'random password'
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 400
        expected_resp_message = UserResponseMessage.TEMPORARY_BLOCKED_EMAIL

        self.assertEqual(self.blocked_otp_obj.attempts_used, OTP_MAX_ATTEMPTS)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('email')[0], expected_resp_message)

    def test_resend_blocked(self):
        """Should be bad request if blocked email hits `/user/sign-up/`
        """
        data = {
            'client_id': self.CLIENT_ID,
            'email': self.resend_blocked_otp_obj.email,
            'password': 'random password'
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 400
        expected_resp_message = UserResponseMessage.OTP_RESENDS_EXCEEDED
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_expired_otp(self):
        """Should be success to resend expired otp
        """
        data = {
            'client_id': self.CLIENT_ID,
            'email': self.expired_otp_obj.email,
            'password': 'random password'
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 200
        expected_resp_message = UserResponseMessage.OTP_SUCCESS

        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_last_successful_resend(self):
        """Should be success with message resend exceeded
        on the last resend request"""
        data = {
            'client_id': self.CLIENT_ID,
            'email': self.almost_resend_blocked_otp_obj.email,
            'password': 'random password'
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 200
        expected_resp_message = UserResponseMessage.OTP_RESENDS_EXCEEDED

        obj = AuthOTP.objects.get(
            email=self.almost_resend_blocked_otp_obj.email)
        self.assertEqual(obj.resends_used, OTP_MAX_RESENDS)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_resend_otp(self):
        """Should be success on resend and return with `email` which requested
        """
        num_resends = self.valid_otp_obj.resends_used
        data = {
            'client_id': self.CLIENT_ID,
            'email': self.valid_otp_obj.email,
            'password': 'random password'
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 200
        expected_resp_message = UserResponseMessage.OTP_SUCCESS

        obj = AuthOTP.objects.get(email=self.valid_otp_obj.email)
        self.assertEqual(obj.resends_used, num_resends + 1)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)


class VerifyOTPAPITestCase(APITestCase):
    """APITestCase class to test `/user/verify-otp/` endpoint.
    """
    CLIENT_ID = "boofar"

    def setUp(self):
        self.user_expired = User.objects.create(username='oort', email='oort@oort.com')
        self.user_correct = User.objects.create(username='toor', email='toor@toor.com')
        self.user_max_attempts = User.objects.create(username='orot', email='orot@orot.com')
        self.user_blocked = User.objects.create(username='toro', email='toro@toro.com')

        app = Application.objects.create(user=self.user_expired, client_id=self.CLIENT_ID)
        self.url = reverse('verify_otp_view')
        self.expired_otp_obj = AuthOTP.objects.create(
            email=self.user_expired.email,
            client=app,
            expires_at=timezone.now()
        )

        self.correct_otp_obj = AuthOTP.get_or_create_otp(self.user_correct.email, app)
        self.max_attempts_otp_obj = AuthOTP.get_or_create_otp(
            self.user_max_attempts.email, app)
        self.blocked_otp_obj = AuthOTP.objects.create(
            email=self.user_blocked.email,
            client=app,
            expires_at=timezone.now() + timedelta(days=1),
            attempts_used=OTP_MAX_ATTEMPTS,
            blocked_until=timezone.now() + timedelta(days=1)
        )

    def test_get_request(self):
        """Should not allow to request with GET at /user/signup/send-otp/
        """
        response = self.client.get(self.url, format='json')
        expected_status_code = 405
        self.assertEqual(response.status_code, expected_status_code)

    def test_invalid_email(self):
        """Should be forbidden for existing users to hit
        `/user/signup/verify-token/`
        """

        data = {
            'client_id': 'boofar',
            'email': 'oort@oort.com',
            'otp': 'random otp',
            'context': OTPVerificationContexts.SIGN_UP.value
        }
        response = self.client.post(self.url, format='json', data=data)

        expected_status_code = 400
        self.assertEqual(response.status_code, expected_status_code)

    def test_bad_client(self):
        """Should handle bad client with a HTTP Bad request: `/user/verify-otp/`
        """
        data = {
            'client_id': 'foobar',
            'email': self.correct_otp_obj.email,
            'otp': 'random otp',
            'context': OTPVerificationContexts.SIGN_UP.value
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 400
        expected_resp_message = UserResponseMessage.BAD_CLIENT
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('client_id')[0], expected_resp_message)

    def test_no_otp(self):
        """Should be a bad request when there is no otp associated with email and client
        """
        data = {
            'client_id': 'boofar',
            'email': 'aaa@aaa.com',
            'otp': 'random otp',
            'context': OTPVerificationContexts.SIGN_UP.value
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 400
        expected_resp_message = ResponseMessages.INVALID_EMAIL
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('email')[0], expected_resp_message)

    def test_blocked_email(self):
        """Should be bad request for blocked email to access: `/user/signup/send-otp/`
        """
        data = {
            'client_id': self.CLIENT_ID,
            'email': self.blocked_otp_obj.email,
            'otp': 'random otp',
            'context': OTPVerificationContexts.SIGN_UP.value
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 400
        expected_resp_message = UserResponseMessage.TEMPORARY_BLOCKED_EMAIL
        self.assertEqual(self.blocked_otp_obj.attempts_used, OTP_MAX_ATTEMPTS)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('email')[0], expected_resp_message)

    def test_expired_otp(self):
        """Should be a bad request if expired token is provided
        """
        data = {
            'client_id': 'boofar',
            'email': self.user_expired.email,
            'otp': 'any otp',
            'context': OTPVerificationContexts.SIGN_UP.value
        }
        response = self.client.post(
            self.url,
            format='json',
            data=data
        )
        expected_status_code = 400
        expected_resp_message = UserResponseMessage.OTP_EXPIRED
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_invalid_otp(self):
        """Should be a bad request if wrong otp is given
        """
        attempts_used = self.correct_otp_obj.attempts_used
        data = {
            'client_id': self.CLIENT_ID,
            'email': self.user_correct.email,
            'otp': 'wrong otp',
            'context': OTPVerificationContexts.SIGN_UP.value
        }
        response = self.client.post(self.url, format='json', data=data)

        expected_status_code = 400
        expected_resp_message = UserResponseMessage.INVALID_OTP

        obj = AuthOTP.objects.get(email=self.correct_otp_obj.email)
        self.assertEqual(obj.attempts_used, attempts_used + 1)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_otp_attempt_limit(self):
        """Should be a bad request if OTP attempts have been exceeded
        """

        data = {
            'client_id': 'boofar',
            'email': self.correct_otp_obj.email,
            'otp': 'wrong otp',
            'context': OTPVerificationContexts.SIGN_UP.value
        }
        response = None
        for _ in range(OTP_MAX_ATTEMPTS):
            response = self.client.post(self.url, format='json', data=data)

        expected_status_code = 400
        expected_resp_message = UserResponseMessage.OTP_ATTEMPT_EXCEEDED

        obj = AuthOTP.objects.get(email=data['email'])
        self.assertEqual(obj.attempts_used, OTP_MAX_ATTEMPTS)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data.get('message'), expected_resp_message)

    def test_correct_otp_attempt(self):
        """Should be a success if OTP matches
        """
        data = {
            'client_id': self.CLIENT_ID,
            'email': self.user_correct.email,
            'otp': self.correct_otp_obj.one_time_code,
            'context': OTPVerificationContexts.SIGN_UP.value
        }
        response = self.client.post(self.url, format='json', data=data)
        expected_status_code = 200
        self.assertEqual(response.status_code, expected_status_code)
        self.assertFalse(AuthOTP.objects.filter(email=self.correct_otp_obj.email).exists())
        self.assertTrue({
            'access_token',
            'refresh_token',
            'expires'
        } < response.data.keys())
