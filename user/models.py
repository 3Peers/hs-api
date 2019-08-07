from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from oauth2_provider.models import Application

from globals.utils.string import generate_random_string
from .constants import (
    OTP_EXPIRY_SECONDS,
    OTP_MAX_ATTEMPTS,
    OTP_MAX_RESENDS,
    EMAIL_BLOCK_SECONDS
)


class User(AbstractUser):
    about = models.TextField(default='', blank=True)
    primary_phone_no = models.CharField(max_length=15, null=True)
    secondary_phone_no = models.CharField(max_length=15, null=True)
    secondary_email = models.EmailField(null=True)
    profile_picture = models.URLField(null=True)
    address = models.TextField(null=True)
    city = models.CharField(max_length=30, null=True)
    state = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def create_basic_user(email):
        user = User.objects.create(**{
            'email': email,
            'password': generate_random_string(12),
            'username': email,
        })

        return user

    @staticmethod
    def get_all_users():
        return User.objects.all()

    @staticmethod
    def get_public_fields():
        return [
            'username',
            'first_name',
            'last_name',
            'profile_picture'
        ]

    def __str__(self):
        return self.username


class SignUpOTP(models.Model):
    client = models.ForeignKey(Application, related_name='otps', on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    one_time_code = models.CharField(max_length=8, blank=False)
    expires_at = models.DateTimeField()
    blocked_until = models.DateTimeField(null=True)
    attempts_used = models.IntegerField(default=0)
    resends_used = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _update_attempts(self):
        if self.is_email_blocked():
            return

        self.attempts_used += 1
        if self.attempts_used >= OTP_MAX_ATTEMPTS:
            self._block_email()

    def _block_email(self, time_now=None):
        if not time_now:
            time_now = timezone.now()
        self.blocked_until = time_now + timedelta(seconds=EMAIL_BLOCK_SECONDS)

    @staticmethod
    def _create_otp_for_email(email: str, client: Application):
        return SignUpOTP.objects.create(**{
            'one_time_code': generate_random_string(8),
            'email': email,
            'expires_at': timezone.now() + timedelta(seconds=OTP_EXPIRY_SECONDS),
            'client': client
        })

    @staticmethod
    def _get_otp_for_email(email: str, client: Application):
        return SignUpOTP.objects.filter(
            email=email,
            client=client
        ).first()

    def reset_expiry(self, time_now=None):
        if not time_now:
            time_now = timezone.now()
        self.expires_at = time_now + timedelta(seconds=OTP_EXPIRY_SECONDS)

    def is_expired(self, time_now=None):
        if not time_now:
            time_now = timezone.now()

        return time_now >= self.expires_at

    def is_email_blocked(self):
        now = timezone.now()
        return self.blocked_until and now <= self.blocked_until

    def validate_otp(self, otp_string: str):
        self._update_attempts()
        return self.one_time_code == otp_string

    def update_resends(self):
        if self.is_email_blocked():
            return
        self.resends_used += 1

    def is_resend_blocked(self):
        return self.resends_used >= OTP_MAX_RESENDS

    def update_otp_for_email(self):
        self.resends_used = 0
        self.one_time_code = generate_random_string(8)

    def num_attempts_left(self):
        return OTP_MAX_ATTEMPTS - self.attempts_used

    @classmethod
    def get_or_create_otp(cls, email: str, client: Application):
        return cls._get_otp_for_email(
            email,
            client
        ) or cls._create_otp_for_email(
            email,
            client
        )

    @classmethod
    def get_otp(cls, email: str, client: Application):
        return cls._get_otp_for_email(email, client)

    def __str__(self):
        return f'{self.email}: {self.one_time_code}'
