from apps.globals.constants import ResponseMessages
from apps.globals.serializers import DynamicFieldsModelSerializer
from apps.globals.utils.string import is_good_password
from enum import Enum
from oauth2_provider.models import Application
from rest_framework import serializers
from .constants import ResponseMessages as UserResponseMessages
from .models import User, AuthOTP


BAD_CLIENT = 'Unrecognized Client'
BAD_PASSWORD_PROVIDED = 'Bad Password Provided. Please follow good password practices'


class OTPVerificationContexts(Enum):
    SIGN_UP = 'SIGN_UP'
    FORGOT_PASSWORD = 'FORGOT_PASSWORD'

    @staticmethod
    def all():
        return [context.value for context in OTPVerificationContexts]


class ValidateClientIdMixin(object):
    def validate_client_id(self, client_id):
        if not Application.objects.filter(client_id=client_id).exists():
            raise serializers.ValidationError(BAD_CLIENT)
        return client_id


class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = User
        exclude = ('created_at', 'updated_at')
        read_only_fields = ('is_superuser', 'is_staff', 'is_active',
                            'groups', 'user_permissions', 'last_login')
        extra_kwargs = {'password': {'write_only': True}}


class SignUpOTPSerializer(serializers.Serializer, ValidateClientIdMixin):
    email = serializers.EmailField()
    client_id = serializers.CharField()
    password = serializers.CharField()

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(UserResponseMessages.USER_WITH_EMAIL_EXISTS)
        otp_obj: AuthOTP = AuthOTP.objects.filter(email=email).first()
        if otp_obj and otp_obj.is_email_blocked():
            raise serializers.ValidationError(UserResponseMessages.TEMPORARY_BLOCKED_EMAIL)

        return email

    def validate_password(self, password):
        if not is_good_password(password):
            raise serializers.ValidationError(BAD_PASSWORD_PROVIDED)
        return password


class TokenVerificationSerializer(serializers.Serializer, ValidateClientIdMixin):
    email = serializers.EmailField()
    client_id = serializers.CharField()
    otp = serializers.CharField()
    context = serializers.CharField()

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError(ResponseMessages.INVALID_EMAIL)
        otp_obj: AuthOTP = AuthOTP.objects.filter(email=email).first()

        if not otp_obj:
            raise serializers.ValidationError(ResponseMessages.INVALID_EMAIL)
        elif otp_obj.is_email_blocked():
            raise serializers.ValidationError(UserResponseMessages.TEMPORARY_BLOCKED_EMAIL)

        return email

    def validate_context(self, context):
        if context not in OTPVerificationContexts.all():
            raise serializers.ValidationError('Invalid context.')


class ForgotPasswordOTPSerializer(serializers.Serializer, ValidateClientIdMixin):
    email = serializers.EmailField()
    client_id = serializers.CharField()

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('No user with this email found.')
        return email


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_current_password(self, current_password):
        user = self.context.get('user')
        if not user or not user.check_password(current_password):
            raise serializers.ValidationError(UserResponseMessages.INVALID_PASSWORD)
        return current_password

    def validate_new_password(self, new_password):
        if not is_good_password(new_password):
            raise serializers.ValidationError(UserResponseMessages.BAD_PASSWORD_PROVIDED)
        return new_password
