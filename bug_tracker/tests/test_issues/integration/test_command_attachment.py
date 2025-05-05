import pytest
from issues.models import Issue, IssueAttachment, IssueComment
from issues.services import command_attachment, query_attachment
from issues.services.exceptions import CommentActionNotPermitted, IssueActionNotPermitted
from tests.factories import fake_attachment, fake_file
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.fixture
def attachment_1(issue_1: Issue) -> IssueAttachment:
    return fake_attachment(issue=issue_1)


@pytest.fixture
def attachment_2(issue_1: Issue, comment_1: IssueComment) -> IssueAttachment:
    return fake_attachment(issue=issue_1, comment=comment_1)


@pytest.mark.django_db
def test_attachment_add_to_issue(issue_1: Issue, user_1: CustomUser) -> None:
    file, extension = fake_file()

    attachment = command_attachment.attachment_add_to_issue(uploaded_by=user_1, issue=issue_1, file=file)

    assert attachment.issue == issue_1
    assert attachment.comment is None
    assert attachment.uploaded_by == user_1
    assert attachment.extension == extension


@pytest.mark.django_db
def test_attachment_add_to_issue_with_not_enough_permission(issue_1: Issue, user_2: CustomUser) -> None:
    file, _ = fake_file()

    with pytest.raises(IssueActionNotPermitted):
        command_attachment.attachment_add_to_issue(uploaded_by=user_2, issue=issue_1, file=file)


@pytest.mark.django_db
def test_attachment_add_to_comment(comment_1: IssueComment, user_1: CustomUser) -> None:
    file, extension = fake_file()

    attachment = command_attachment.attachment_add_to_comment(uploaded_by=user_1, comment=comment_1, file=file)

    assert attachment.issue == comment_1.issue
    assert attachment.comment == comment_1
    assert attachment.uploaded_by == user_1
    assert attachment.extension == extension


@pytest.mark.django_db
def test_attachment_add_to_comment_with_not_enough_permission(comment_1: IssueComment, user_2: CustomUser) -> None:
    file, _ = fake_file()

    with pytest.raises(CommentActionNotPermitted):
        command_attachment.attachment_add_to_comment(uploaded_by=user_2, comment=comment_1, file=file)


@pytest.mark.django_db
def test_issue_attachment_remove(attachment_1: IssueAttachment, issue_1: Issue, user_1: CustomUser) -> None:
    attachment_id = attachment_1.id

    command_attachment.attachment_remove(attachment=attachment_1, requestor=user_1)

    attachment = query_attachment.attachment_get(attachment_id=attachment_id, issue_id=issue_1.id, user=user_1)
    assert attachment is None


@pytest.mark.django_db
def test_comment_attachment_remove(
    attachment_2: IssueAttachment, issue_1: Issue, comment_1: IssueComment, user_1: CustomUser
) -> None:
    attachment_id = attachment_2.id

    command_attachment.attachment_remove(attachment=attachment_2, requestor=user_1)

    attachment = query_attachment.attachment_get(attachment_id=attachment_id, issue_id=issue_1.id, user=user_1)
    assert attachment is None


@pytest.mark.django_db
def test_issue_attachment_remove_with_not_enough_permission(attachment_1: IssueAttachment, user_2: CustomUser) -> None:
    with pytest.raises(IssueActionNotPermitted):
        command_attachment.attachment_remove(attachment=attachment_1, requestor=user_2)


@pytest.mark.django_db
def test_comment_attachment_remove_with_not_enough_permission(
    attachment_2: IssueAttachment, user_2: CustomUser
) -> None:
    with pytest.raises(CommentActionNotPermitted):
        command_attachment.attachment_remove(attachment=attachment_2, requestor=user_2)
