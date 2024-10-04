import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from .utils import generate_unique_code

UserModel = get_user_model()


class LogBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="%(class)s_created_by",
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="%(class)s_updated_by",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class BaseModel(LogBase):
    code = models.CharField(
        max_length=128, help_text=_("Unique reference by the user")
    )
    is_available = models.BooleanField(
        default=True, help_text=_("if TRUE the record is available")
    )

    def __str__(self):
        return self.code

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["code"]),
        ]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.code:
            self.code = generate_unique_code()
        super().save(force_insert, force_update, using, update_fields)


class UUIDBaseModel(LogBase):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
