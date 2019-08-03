from contextlib import contextmanager


@contextmanager
def authenticated_user_api_client(client, user):
    yield client.force_authenticate(user=user)
    client.force_authenticate(user=None)
