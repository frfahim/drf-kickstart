import datetime
from config.env import env

SIMPLE_JWT = {
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("JWT",),
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(
        seconds=env.int("ACCESS_TOKEN_LIFETIME")
    ),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(
        seconds=env.int("REFRESH_TOKEN_LIFETIME")
    ),
}

# https://github.com/iMerica/dj-rest-auth
REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "kickstart-app-auth",
    "JWT_AUTH_REFRESH_COOKIE": "kickstart-refresh-token",
    "SESSION_LOGIN": False,
    "JWT_AUTH_SECURE": True, # the cookie will only be sent through https scheme.
    "JWT_AUTH_HTTPONLY": False,
    "USER_DETAILS_SERIALIZER": "apps.users.api.serializers.AuthUserDetailsSerializer"
}
