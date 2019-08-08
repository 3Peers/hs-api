from rest_framework.throttling import UserRateThrottle


class UserExistenceViewThrottle(UserRateThrottle):
    scope = 'user_exists_endpoint'
