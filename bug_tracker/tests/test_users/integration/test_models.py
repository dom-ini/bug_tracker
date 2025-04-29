import pytest
from allauth.account.models import EmailAddress
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_create_superuser_with_existing_email_should_fail(user_with_verified_email: CustomUser) -> None:
    with pytest.raises(ValueError):
        CustomUser.objects.create_superuser(
            username="username", email=user_with_verified_email.email, password="P@ssword1234"
        )


@pytest.mark.django_db
def test_create_superuser_creates_user_with_verified_email() -> None:
    email = "user@example.com"
    username = "username"
    password = "P@ssword1234"

    superuser = CustomUser.objects.create_superuser(username=username, email=email, password=password)

    assert superuser.email == email
    assert superuser.username == username
    assert superuser.check_password(password)
    assert EmailAddress.objects.filter(user=superuser, email=email, verified=True).exists()
