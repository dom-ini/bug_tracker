from typing import Any

from allauth.account.models import EmailAddress
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    def create_superuser(
        self,
        username: str,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ):
        if email and EmailAddress.objects.is_verified(email):
            raise ValueError(_("Email address is already taken"))
        user = super().create_superuser(username, email, password, **extra_fields)
        EmailAddress.objects.get_or_create(user=user, email=email, verified=True, primary=True)
        return user


class CustomUser(AbstractUser):
    objects = CustomUserManager()

    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    class Meta:
        db_table = "users_user"
        verbose_name = _("user")
        verbose_name_plural = _("users")
