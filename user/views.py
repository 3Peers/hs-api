from datetime import timedelta
from django.utils import timezone
from globals.utils.string import is_valid_email, is_good_password
from globals.utils.email import send_mail
from globals.constants import ResponseMessages
from globals.serializers import get_serializer_with_fields
from oauth2_provider.models import Application, AccessToken, RefreshToken
from oauth2_provider.settings import oauth2_settings
from oauthlib import common
from rest_framework import exceptions, generics, views, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from .models import User, SignUpOTP
from .serializers import UserSerializer
from .throttle import UserExistenceViewThrottle
from .utils import get_verification_message_with_code

TEMPORARY_BLOCKED_EMAIL = 'This email has been temporarily blocked.' \
        ' Please try after some time'
BAD_CLIENT = 'Unrecognized Client'
INVALID_OTP = 'Entered OTP wrong. Please Try Again.'
OTP_ATTEMPT_EXCEEDED = 'OTP attempts limit exceeded. Please try after some time.'
OTP_RESENDS_EXCEEDED = 'OTP resends limit exceeded. Please try after some time.'
OTP_SUCCESS = 'OTP Sent Successfully.'
OTP_EXPIRED = 'OTP has expired'
RESET_PASSWORD_SUCCESS = 'Password Reset Successfully'
BAD_PASSWORD_PROVIDED = 'Bad Password Provided. Please follow good password practices'
NO_USER_FOUND = 'No User Found'


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
            raise exceptions.NotFound(NO_USER_FOUND)

        return Response(True)


class SendOTPView(views.APIView):
    permission_classes = (AllowAny,)

    def send_otp(self, otp):
        email_subject = 'HS: Please Verify your Email'
        verification_message = get_verification_message_with_code(
            otp.one_time_code)

        send_mail.delay(
            email_subject,
            verification_message,
            [otp.email]
        )

    def post(self, request: Request):
        email = request.data.get('email')
        client_id = request.data.get('client_id')

        client = Application.objects.filter(client_id=client_id).first()

        if not client:
            return Response({
                'message': BAD_CLIENT
            }, status=status.HTTP_403_FORBIDDEN)

        if not is_valid_email(email):
            return Response({
                'message': ResponseMessages.INVALID_EMAIL
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response(status=status.HTTP_403_FORBIDDEN)

        otp: SignUpOTP = SignUpOTP.get_or_create_otp(
            email,
            client
        )

        error_message = None
        if otp.is_email_blocked():
            error_message = TEMPORARY_BLOCKED_EMAIL
        elif otp.is_resend_blocked():
            error_message = OTP_RESENDS_EXCEEDED

        if error_message:
            return Response({
                'message': error_message
            }, status.HTTP_403_FORBIDDEN)

        if otp.is_expired():
            otp.update_otp_for_email()
            otp.reset_expiry()

        otp.update_resends()
        otp.save()
        self.send_otp(otp)

        message = OTP_SUCCESS
        if otp.is_resend_blocked():
            message = OTP_RESENDS_EXCEEDED

        return Response({'message': message})


class VerifyOTPView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request):
        email = request.data.get('email')
        client_id = request.data.get('client_id')
        otp_string = request.data.get('otp')

        if is_valid_email(email) and User.objects.filter(email=email).exists():
            return Response(status=status.HTTP_403_FORBIDDEN)

        client = Application.objects.filter(client_id=client_id).first()
        if not client:
            return Response({
                'message': BAD_CLIENT
            }, status=status.HTTP_403_FORBIDDEN)

        otp: SignUpOTP = SignUpOTP.get_otp(email, client)

        if not otp:
            return Response({
                'message': ResponseMessages.BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        elif otp.is_email_blocked():
            return Response({
                'message': TEMPORARY_BLOCKED_EMAIL
            }, status=status.HTTP_403_FORBIDDEN)

        elif otp.is_expired():
            return Response({
                'message': OTP_EXPIRED
            }, status.HTTP_400_BAD_REQUEST)

        otp_valid = otp.validate_otp(otp_string)
        otp.save()

        if not otp_valid:
            error_message = INVALID_OTP

            if otp.is_email_blocked():
                error_message = OTP_ATTEMPT_EXCEEDED

            return Response({
                'message': error_message,
                'attempts_left': otp.num_attempts_left()
            }, status=status.HTTP_400_BAD_REQUEST)

        otp.delete()

        token_response = self._generate_token_response(email, client)
        return Response(token_response)

    def _generate_token_response(self, email: str, client):
        user: User = User.create_basic_user(email)
        user.is_active = False
        user.save()

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
        password = request.data.get('password')

        if is_good_password(password):
            self.request.user.set_password(password)
            return Response({'message': RESET_PASSWORD_SUCCESS})

        return Response({
            'message': BAD_PASSWORD_PROVIDED
        }, status.HTTP_400_BAD_REQUEST)
