import pytest
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from issues.models import Issue, IssueAttachment
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_issue_url(attachment: IssueAttachment) -> None:
    assert attachment.url == attachment.file.url


@pytest.mark.django_db
def test_file_is_deleted_with_attachment_instance(issue: Issue, user_with_verified_email: CustomUser) -> None:
    extension = "txt"
    file = ContentFile(b"hello", name=f"hello.{extension}")
    attachment = IssueAttachment(file=file, extension=extension, issue=issue, uploaded_by=user_with_verified_email)
    attachment.save()
    file_name = attachment.file.name

    assert default_storage.exists(file_name)

    attachment.delete()

    assert not default_storage.exists(file_name)
