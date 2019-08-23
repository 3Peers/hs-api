from datetime import timedelta
from django.utils import timezone
from apps.globals.utils.email import send_mail
from apps.globals.constants import ResponseMessages
from apps.globals.serializers import get_serializer_with_fields
from oauth2_provider.models import Application, AccessToken, RefreshToken
from oauth2_provider.settings import oauth2_settings
from oauthlib import common
from rest_framework import exceptions, generics, views, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from .constants import ResponseMessages as UserResponseMessages
from .exceptions import AuthOTPException
from .models import User, AuthOTP
from .serializers import (
    UserSerializer,
    SignUpOTPSerializer,
    TokenVerificationSerializer,
    ForgotPasswordOTPSerializer,
    ChangePasswordSerializer,
    OTPVerificationContexts
)
from .throttle import UserExistenceViewThrottle
from .utils import get_verification_message_with_code, get_password_reset_message_with_code


class UserRetrieveView(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = User.get_all_users().filter(is_active=True)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        fields_to_send = User.get_public_fields()

        if self.request.user.id == self.kwargs.get('pk'):
            fields_to_send = '__all__'
        return get_serializer_with_fields(UserSerializer, fields=fields_to_send)


class GetCurrentUserView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        fields_to_send = ['id', 'username', 'email', 'first_name', 'last_name']
        serializer = UserSerializer(request.user, fields=fields_to_send)
        return Response(serializer.data)


class CheckUserExistsView(views.APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (UserExistenceViewThrottle,)

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(email=email)
        if not users:
            raise exceptions.NotFound(UserResponseMessages.NO_USER_FOUND)

        return Response({
            'exists': True
        })


class SignUpSendOTPView(views.APIView):
    permission_classes = (AllowAny,)

    def _send_otp(self, otp):
        email_subject = 'HS: Please Verify your Email'
        verification_message = get_verification_message_with_code(
            otp.one_time_code)

        send_mail.delay(
            email_subject,
            verification_message,
            [otp.email]
        )

    def post(self, request: Request):
        serializer = SignUpOTPSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            pass

        email = serializer.validated_data.get('email')
        client_id = serializer.validated_data.get('client_id')
        password = serializer.validated_data.get('password')

        client = Application.objects.get(client_id=client_id)

        try:
            otp = AuthOTP.generate_otp(email=email, client=client)
            self._send_otp(otp)

            message = UserResponseMessages.OTP_SUCCESS
            if otp.is_resend_blocked():
                message = UserResponseMessages.OTP_RESENDS_EXCEEDED

            self._create_user(email, password)
            return Response({'message': message})
        except AuthOTPException as ex:
            return Response({'message': str(ex)}, status.HTTP_400_BAD_REQUEST)

    def _create_user(self, email, password):
        if not User.objects.filter(email=email).exists():
            User.create_basic_user(email=email, password=password, is_active=False)


class ForgotPasswordSendOTPView(views.APIView):
    permission_classes = (AllowAny,)

    def _send_otp(self, otp):
        email_subject = 'HS: OTP for Password Reset'
        message = get_password_reset_message_with_code(
            otp.one_time_code)

        send_mail.delay(
            email_subject,
            message,
            [otp.email]
        )

    def post(self, request: Request):
        serializer = ForgotPasswordOTPSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            pass

        email = serializer.validated_data.get('email')
        client_id = serializer.validated_data.get('client_id')

        client = Application.objects.get(client_id=client_id)
        try:
            otp = AuthOTP.generate_otp(email=email, client=client)

            self._send_otp(otp)
            message = UserResponseMessages.OTP_SUCCESS
            if otp.is_resend_blocked():
                message = UserResponseMessages.OTP_RESENDS_EXCEEDED

            return Response({'message': message})

        except AuthOTPException as ex:
            return Response({'message': str(ex)}, status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request):
        serializer = TokenVerificationSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            pass

        email = serializer.validated_data.get('email')
        client_id = serializer.validated_data.get('client_id')
        otp_string = serializer.validated_data.get('otp')
        context = serializer.validated_data.get('context')

        client = Application.objects.get(client_id=client_id)

        otp: AuthOTP = AuthOTP.get_otp(email, client)

        if not otp:
            return Response({
                'message': ResponseMessages.BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        elif otp.is_email_blocked():
            return Response({
                'message': UserResponseMessages.TEMPORARY_BLOCKED_EMAIL
            }, status=status.HTTP_403_FORBIDDEN)

        elif otp.is_expired():
            return Response({
                'message': UserResponseMessages.OTP_EXPIRED
            }, status.HTTP_400_BAD_REQUEST)

        otp_valid = otp.validate_otp(otp_string)
        otp.save()

        if not otp_valid:
            error_message = UserResponseMessages.INVALID_OTP

            if otp.is_email_blocked():
                error_message = UserResponseMessages.OTP_ATTEMPT_EXCEEDED

            return Response({
                'message': error_message,
                'attempts_left': otp.num_attempts_left()
            }, status=status.HTTP_400_BAD_REQUEST)

        otp.delete()
        user = self._get_user_for_context(otp, context)
        token_response = self._generate_token_response(user, client)
        return Response(token_response)

    def _get_user_for_context(self, otp, context):
        user = User.objects.get(email=otp.email)

        if context == OTPVerificationContexts.SIGN_UP:
            user.is_active = True
            user.save()
        return user

    def _generate_token_response(self, user: User, client):
        expires = timezone.now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        access_token = AccessToken(
            user=user,
            scope='read write',
            expires=expires,
            token=common.generate_token(),
            application=client
        )
        access_token.save()
        refresh_token = RefreshToken(
            user=user,
            token=common.generate_token(),
            application=client,
            access_token=access_token
        )
        refresh_token.save()

        return {
            'access_token': access_token.token,
            'scope': access_token.scope,
            'expires': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            'refresh_token': refresh_token.token,
            'token_type': 'Bearer'
        }


class ChangePasswordView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
        if not serializer.is_valid(raise_exception=True):
            pass

        password = serializer.validated_data.get('new_password')

        self.request.user.set_password(password)
        self.request.user.save()
        return Response({'message': UserResponseMessages.RESET_PASSWORD_SUCCESS})
