from rest_framework import serializers

from apps.users.models import User
from dj_rest_auth.serializers import UserDetailsSerializer as DJRestUserDetailsSerializer

class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["username", "name"]


class AuthUserDetailsSerializer(DJRestUserDetailsSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "name",
        ]
