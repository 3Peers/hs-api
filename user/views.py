from datetime import timedelta
from django.utils import timezone
from globals.utils.string import is_valid_email
from globals.utils.email import send_mail
from globals.constants import ResponseMessages
from oauth2_provider.models import Application, AccessToken, RefreshToken
from oauth2_provider.settings import oauth2_settings
from oauthlib import common
from rest_framework import generics, views, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from .models import User, SignUpOTP
from .serializers import UserSerializer
from .utils import get_verification_message_with_code

TEMPORARY_BLOCKED_EMAIL = 'This email has been temporarily blocked.' \
        ' Please try after some time'
BAD_CLIENT = 'Unrecognized Client'
INVALID_OTP = 'Entered OTP wrong. Please Try Again.'
OTP_ATTEMPT_EXCEEDED = 'OTP attempts limit exceeded. Please try after some time.'
OTP_SUCCESS = 'OTP Sent Successfully.'


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.get_all_users()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination


class UserRetrieveDeleteView(generics.RetrieveDestroyAPIView):
    lookup_field = 'pk'
    queryset = User.get_all_users()
    serializer_class = UserSerializer


class GetCurrentUserView(views.APIView):

    def get(self, request):
        return Response({
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        })


class SendOTPView(views.APIView):
    permission_classes = (AllowAny,)

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

        otp: SignUpOTP = SignUpOTP.get_existing_otp_or_none(email, client)

        if not otp:
            otp: SignUpOTP = SignUpOTP.create_otp_for_email(email, client)
        elif otp.is_blocked():
            return Response({
                'message': TEMPORARY_BLOCKED_EMAIL
            }, status.HTTP_403_FORBIDDEN)
        elif otp.is_expired():
            otp.update_otp_for_email()
        else:
            otp._update_resends()
            otp.save()

        verification_message = get_verification_message_with_code(otp.one_time_code)
        send_mail.delay('HS: Please Verify your Email', verification_message, [otp.email])

        return Response({
            'message': OTP_SUCCESS
        })


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

        otp: SignUpOTP = SignUpOTP.get_existing_otp_or_none(email, client)

        if not otp:
            return Response({
                'message': ResponseMessages.BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        if otp.is_blocked():
            return Response({
                'message': TEMPORARY_BLOCKED_EMAIL
            }, status=status.HTTP_403_FORBIDDEN)

        otp_valid = otp.validate_otp(otp_string)
        otp.save()

        if not otp_valid:
            error_message = INVALID_OTP

            if otp.is_blocked():
                error_message = OTP_ATTEMPT_EXCEEDED

            return Response({
                'message': error_message
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
