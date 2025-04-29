import pytest
from users.forms import CustomSetPasswordForm
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_valid_password_sets_user_password(user_with_verified_email: CustomUser) -> None:
    new_password = "NewStrongPass123!"
    form = CustomSetPasswordForm(user_with_verified_email, data={"new_password": new_password})

    assert form.is_valid()
    form.save()

    assert user_with_verified_email.check_password(new_password)


@pytest.mark.django_db
def test_invalid_password_fails_validation(user_with_verified_email: CustomUser) -> None:
    form = CustomSetPasswordForm(user_with_verified_email, data={"new_password": "weak"})

    assert not form.is_valid()
    assert "new_password" in form.errors
