import random

from allauth.account.models import EmailAddress
from faker import Faker
from projects.models import Project
from projects.services.command_project import project_create
from users.models import CustomUser

fake = Faker()


def fake_user(*, password: str | None = None, is_verified: bool = True) -> CustomUser:
    password = password or fake.password(length=15, lower_case=True, upper_case=True, digits=True, special_chars=True)
    user = CustomUser.objects.create_user(username=fake.user_name(), email=fake.email(), password=password)
    EmailAddress.objects.create(user=user, email=user.email, verified=is_verified, primary=True)
    return user


def fake_project(*, user: CustomUser) -> Project:
    subdomain = fake.domain_word() + str(random.randint(1000, 9999))
    return project_create(
        name=fake.sentence(nb_words=4), description=fake.sentence(nb_words=20), subdomain=subdomain, user=user
    )
