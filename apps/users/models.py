from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
