import jwt
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.core.cache import cache


User = get_user_model()
JWT_SETTINGS = getattr(settings, 'SIMPLE_JWT', {})


class EcommerceJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.META.get('HTTP_AUTHORIZATION')
        if not header:
            return None

        try:
            prefix, token = header.split()
        except ValueError:
            raise AuthenticationFailed('Header parsing error')

        if prefix not in JWT_SETTINGS.get('AUTH_HEADER_TYPES', ('Bearer', )):
            return None

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed(
                'Token has expired (=',
                code='token_expired'
            )
        except jwt.InvalidTokenError:
            raise AuthenticationFailed(
                'Invalid token, try again!',
                code='invalid_token'
            )

        if payload.get('token_type') != 'access':
            raise AuthenticationFailed(
                'Invalid token type',
                code='invalid_token_type'
            )

        try:
            user_payload = {key: payload.get(key) for key in JWT_SETTINGS.get(
                'USER_ID_FIELDS', ['id']
            )}
            user = User.objects.get(**user_payload)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found', code='invalid_user')

        return (user, token)
