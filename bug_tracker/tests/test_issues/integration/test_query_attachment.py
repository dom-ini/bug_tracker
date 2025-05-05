import pytest
from issues.models import Issue, IssueAttachment, IssueComment
from issues.services import query_attachment
from tests.factories import fake_attachment
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.fixture
def attachment_1(issue_1: Issue) -> IssueAttachment:
    return fake_attachment(issue=issue_1)


@pytest.fixture
def attachment_2(issue_1: Issue, comment_1: IssueComment) -> IssueAttachment:
    return fake_attachment(issue=issue_1, comment=comment_1)


@pytest.mark.django_db
def test_attachment_get_returns_correct_attachment(
    issue_1: Issue, attachment_1: IssueAttachment, user_1: CustomUser
) -> None:
    attachment = query_attachment.attachment_get(attachment_id=attachment_1.id, issue_id=issue_1.id, user=user_1)

    assert attachment.id == attachment_1.id
    assert attachment.issue == issue_1
    assert attachment.file.name == attachment_1.file.name


@pytest.mark.django_db
def test_attachment_get_returns_none_if_requestor_not_part_of_project(
    issue_1: Issue, attachment_1: IssueAttachment, user_2: CustomUser
) -> None:
    attachment = query_attachment.attachment_get(attachment_id=attachment_1.id, issue_id=issue_1.id, user=user_2)

    assert attachment is None


@pytest.mark.django_db
def test_attachment_get_returns_none_if_invalid_issue_id(attachment_1: IssueAttachment, user_1: CustomUser) -> None:
    attachment = query_attachment.attachment_get(attachment_id=attachment_1.id, issue_id=999, user=user_1)

    assert attachment is None


@pytest.mark.django_db
def test_attachment_get_returns_none_if_invalid_attachment_id(issue_1: Issue, user_1: CustomUser) -> None:
    attachment = query_attachment.attachment_get(attachment_id=999, issue_id=issue_1.id, user=user_1)

    assert attachment is None


@pytest.mark.django_db
def test_attachment_list_all_returns_all_issue_attachments(
    issue_1: Issue, attachment_1: IssueAttachment, attachment_2: IssueAttachment, user_1: CustomUser
) -> None:
    attachments = query_attachment.attachment_list_all(issue_id=issue_1.id, user=user_1)

    attachment_ids = {a.id for a in attachments}
    assert attachments.count() == 2
    assert attachment_1.id in attachment_ids
    assert attachment_2.id in attachment_ids


@pytest.mark.django_db
def test_attachment_list_for_issue_returns_only_issue_attachments(
    issue_1: Issue, attachment_1: IssueAttachment, attachment_2: IssueAttachment, user_1: CustomUser
) -> None:
    attachments = query_attachment.attachment_list_for_issue(issue_id=issue_1.id, user=user_1)

    attachment_ids = {a.id for a in attachments}
    assert attachments.count() == 1
    assert attachment_1.id in attachment_ids


@pytest.mark.django_db
def test_attachment_list_for_comment_returns_only_comment_attachments(
    issue_1: Issue,
    comment_1: IssueComment,
    attachment_1: IssueAttachment,
    attachment_2: IssueAttachment,
    user_1: CustomUser,
) -> None:
    attachments = query_attachment.attachment_list_for_comment(
        issue_id=issue_1.id, comment_id=comment_1.id, user=user_1
    )

    attachment_ids = {a.id for a in attachments}
    assert attachments.count() == 1
    assert attachment_2.id in attachment_ids


@pytest.mark.django_db
def test_attachment_list_all_returns_empty_if_requestor_not_part_of_project(
    issue_1: Issue, attachment_1: IssueAttachment, attachment_2: IssueAttachment, user_2: CustomUser
) -> None:
    attachments = query_attachment.attachment_list_all(issue_id=issue_1.id, user=user_2)

    assert attachments.count() == 0


@pytest.mark.django_db
def test_attachment_list_for_issue_returns_empty_if_requestor_not_part_of_project(
    issue_1: Issue, attachment_1: IssueAttachment, attachment_2: IssueAttachment, user_2: CustomUser
) -> None:
    attachments = query_attachment.attachment_list_for_issue(issue_id=issue_1.id, user=user_2)

    assert attachments.count() == 0


@pytest.mark.django_db
def test_attachment_list_for_comment_returns_empty_if_requestor_not_part_of_project(
    issue_1: Issue,
    comment_1: IssueComment,
    attachment_1: IssueAttachment,
    attachment_2: IssueAttachment,
    user_2: CustomUser,
) -> None:
    attachments = query_attachment.attachment_list_for_comment(
        comment_id=comment_1.id, issue_id=issue_1.id, user=user_2
    )

    assert attachments.count() == 0


@pytest.mark.django_db
def test_attachment_list_all_returns_empty_if_invalid_issue_id(user_1: CustomUser) -> None:
    issues = query_attachment.attachment_list_all(issue_id=999, user=user_1)

    assert issues.count() == 0


@pytest.mark.django_db
def test_attachment_list_for_issue_returns_empty_if_invalid_issue_id(user_1: CustomUser) -> None:
    issues = query_attachment.attachment_list_for_issue(issue_id=999, user=user_1)

    assert issues.count() == 0


@pytest.mark.django_db
def test_attachment_list_for_comment_returns_empty_if_invalid_issue_id(
    comment_1: IssueComment, attachment_2: IssueAttachment, user_1: CustomUser
) -> None:
    issues = query_attachment.attachment_list_for_comment(comment_id=comment_1.id, issue_id=999, user=user_1)

    assert issues.count() == 0


@pytest.mark.django_db
def test_attachment_list_for_comment_returns_empty_if_invalid_comment_id(
    issue_1: Issue, attachment_2: IssueAttachment, user_1: CustomUser
) -> None:
    issues = query_attachment.attachment_list_for_comment(comment_id=999, issue_id=issue_1.id, user=user_1)

    assert issues.count() == 0
