from apps.globals.managers.test_managers import authenticated_user_api_client
from django.shortcuts import reverse
from rest_framework.test import APITestCase
from ..models import User
from ..constants import ResponseMessages


class ChangePasswordViewTestCase(APITestCase):
    USER_PASSWORD = 'the password'

    def setUp(self):
        self.user = User.objects.create_user(
            username='username',
            email='email@email.com',
            password=self.USER_PASSWORD
        )

        self.url = reverse('change_password')

    def test_unauthenticated_request(self):
        """Should not allow unauthorized access /user/change-password/
        """
        data = {
            'current_password': self.USER_PASSWORD,
            'new_password': '1234567891011'
        }
        response = self.client.post(self.url, data=data)

        expected_response_code = 401
        self.assertEqual(response.status_code, expected_response_code)

    def test_wrong_current_password(self):
        """Should be a bad request if wrong password provided
        """
        data = {
            'current_password': self.USER_PASSWORD + 'random string',
            'new_password': 'some random new password'
        }

        with authenticated_user_api_client(self.client, self.user):
            response = self.client.post(self.url, data=data)
            expected_response_code = 400
            expected_message = ResponseMessages.INVALID_PASSWORD

            self.assertEqual(response.status_code, expected_response_code)
            self.assertEqual(response.data.get('current_password')[0], expected_message)

    def test_bad_new_password(self):
        """Should be a bad request if bad password provided \
        (not following strong password practices) at /user/change-password/
        """
        data = {
            'current_password': self.USER_PASSWORD,
            'new_password': '1234'
        }

        with authenticated_user_api_client(self.client, self.user):
            response = self.client.post(self.url, data=data)
            expected_response_code = 400
            expected_message = ResponseMessages.BAD_PASSWORD_PROVIDED

            self.assertEqual(response.status_code, expected_response_code)
            self.assertEqual(response.data.get('new_password')[0], expected_message)

    def test_successful_password_change(self):
        """Should change password successfully /user/change-password/
        """
        data = {
            'current_password': self.USER_PASSWORD,
            'new_password': '1234567891011'
        }

        with authenticated_user_api_client(self.client, self.user):
            response = self.client.post(self.url, data=data)
            expected_response_code = 200
            expected_message = ResponseMessages.RESET_PASSWORD_SUCCESS

            self.assertEqual(response.status_code, expected_response_code)
            self.assertEqual(response.data.get('message'), expected_message)

            self.assertTrue(self.user.check_password(data['new_password']))
