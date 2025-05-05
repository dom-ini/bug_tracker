import random

from allauth.account.models import EmailAddress
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from issues.models import Issue, IssueAttachment, IssueComment
from issues.services.command_comment import comment_create
from issues.services.command_issue import issue_create
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


def fake_issue(*, project: Project, user: CustomUser, assigned_to_id: int | None = None) -> Issue:
    issue_type = random.choice(Issue.Type.choices)[0]
    issue_priority = random.choice(Issue.Priority.choices)[0]
    return issue_create(
        project=project,
        created_by=user,
        assigned_to_id=assigned_to_id,
        title=fake.sentence(nb_words=10),
        description=fake.sentence(nb_words=20),
        priority=issue_priority,
        issue_type=issue_type,
    )


def fake_comment(*, issue: Issue, author: CustomUser) -> IssueComment:
    return comment_create(issue=issue, author=author, text=fake.sentence(nb_words=10))


def fake_file() -> tuple[File, str]:
    extension = "txt"
    file_name = fake.file_name(extension=extension)
    content = fake.sentence(nb_words=10).encode("utf-8")
    file = SimpleUploadedFile(file_name, content=content, content_type="text/plain")
    return file, extension


def fake_attachment(*, issue: Issue, comment: IssueComment | None = None) -> IssueAttachment:
    file, extension = fake_file()
    return IssueAttachment.objects.create(
        issue=issue, comment=comment, uploaded_by=issue.created_by, file=file, extension=extension
    )
