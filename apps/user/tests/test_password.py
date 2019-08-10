from django.shortcuts import reverse
from rest_framework.test import APITestCase
from model_mommy import mommy
from apps.globals.managers.test_managers import authenticated_user_api_client
from ..views import (
    BAD_PASSWORD_PROVIDED,
    RESET_PASSWORD_SUCCESS,
)


class ChangePasswordViewTestCase(APITestCase):

    def setUp(self):
        self.user = mommy.make('user.User')
        self.url = reverse('change_password')

    def test_unauthenticated_request(self):
        """Should not allow unauthorized access /user/change-password/
        """
        data = {'password': '123'}
        response = self.client.post(self.url, data=data)

        expected_response_code = 401
        self.assertEqual(response.status_code, expected_response_code)

    def test_bad_password(self):
        """Should be a bad request if bad password provided \
        (not following strong password practices) at /user/change-password/
        """
        data = {'password': '123'}
        with authenticated_user_api_client(self.client, self.user):
            response = self.client.post(self.url, data=data)

            expected_response_code = 400
            expected_message = BAD_PASSWORD_PROVIDED
            self.assertEqual(response.status_code, expected_response_code)
            self.assertEqual(response.data.get('message'), expected_message)

    def test_successful_password_change(self):
        """Should change password successfully /user/change-password/
        """
        data = {'password': 'hello12345'}
        with authenticated_user_api_client(self.client, self.user):
            response = self.client.post(self.url, data=data)

            expected_response_code = 200
            expected_message = RESET_PASSWORD_SUCCESS
            self.assertEqual(response.status_code, expected_response_code)
            self.assertEqual(response.data.get('message'), expected_message)

            self.assertTrue(self.user.check_password(data['password']))
