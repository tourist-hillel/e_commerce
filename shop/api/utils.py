import jwt
from django.conf import settings
from datetime import datetime, timedelta, timezone


JWT_SETTINGS = getattr(settings, 'SIMPLE_JWT', {})
ACCESS_TOKEN_LIFETIME = JWT_SETTINGS.get('ACCESS_TOKEN_LIFETIME', timedelta(minutes=2))
REFRESH_TOKEN_LIFETIME = JWT_SETTINGS.get('REFRESH_TOKEN_LIFETIME', timedelta(minutes=4))


def populate_user_fields(payload, user):
    for key in JWT_SETTINGS.get('USER_ID_FIELDS', ['id']):
        payload[key] = getattr(user, key)
    return payload


def create_access_token(user):
    token_payload = {
        'exp': datetime.now(timezone.utc) + ACCESS_TOKEN_LIFETIME,
        'iat': datetime.now(timezone.utc),
        'token_type': 'access'
    }
    return jwt.encode(
        populate_user_fields(token_payload, user),
        settings.SECRET_KEY, algorithm='HS256'
    )


def create_refresh_token(user):
    token_payload = {
        'exp': datetime.now(timezone.utc) + REFRESH_TOKEN_LIFETIME,
        'iat': datetime.now(timezone.utc),
        'token_type': 'refresh'
    }
    return jwt.encode(
        populate_user_fields(token_payload, user),
        settings.SECRET_KEY, algorithm='HS256'
    )
