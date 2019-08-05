from django.shortcuts import reverse
from globals.managers.test_managers import authenticated_user_api_client
from rest_framework.test import APITestCase
from ..models import User


class RetrieveUserTestCase(APITestCase):

    def get_url(self, user_id):
        return reverse('get_user_view', kwargs={'pk': user_id})

    def setUp(self):
        self.inactive_user = User.objects.create_user(
            username='inactive',
            email='email@email.com',
            password='random text',
            is_active=False
        )

        self.active_user = User.objects.create_user(
            username='active',
            email='active@email.com',
            password='random test'
        )

    def test_unauthenticated_request(self):
        """Should not be accessible without authentication /user/<pk>/
        """
        url = self.get_url(self.active_user.id)
        response = self.client.get(url)

        expected_status_code = 401
        self.assertEqual(response.status_code, expected_status_code)

    def test_getting_inactive_user(self):
        """Should return HTTP 404 NOT FOUND if inactive user is requested at /user/<pk>/
        """
        url = self.get_url(self.inactive_user.id)
        with authenticated_user_api_client(self.client, self.active_user):
            expected_response_code = 404
            response = self.client.get(url)

            self.assertEqual(response.status_code, expected_response_code)

    def test_get_other_user(self):
        """Should return only public fields for other user at /user/<pk>
        """
        url = self.get_url(self.inactive_user.id)
        self.inactive_user.is_active = True
        self.inactive_user.save()

        with authenticated_user_api_client(self.client, self.active_user):
            expected_response_code = 200
            expected_fields = set(User.get_public_fields())
            response = self.client.get(url)

            response_fields = set(response.data.keys())
            self.assertEqual(response.status_code, expected_response_code)
            self.assertEqual(response_fields, expected_fields)
