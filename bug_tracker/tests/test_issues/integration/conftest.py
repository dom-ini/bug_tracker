import pytest
from issues.models import Issue, IssueAttachment, IssueComment
from projects.models import Project
from tests.factories import fake_attachment, fake_comment, fake_issue, fake_project, fake_user
from users.models import CustomUser


@pytest.fixture
def user_1() -> CustomUser:
    return fake_user()


@pytest.fixture
def user_2() -> CustomUser:
    return fake_user()


@pytest.fixture
def project_1(user_1: CustomUser) -> Project:
    return fake_project(user=user_1)


@pytest.fixture
def issue_1(project_1: Project, user_1: CustomUser) -> Issue:
    return fake_issue(project=project_1, user=user_1)


@pytest.fixture
def issue_2(project_1: Project, user_1: CustomUser) -> Issue:
    return fake_issue(project=project_1, user=user_1)


@pytest.fixture
def comment_1(issue_1: Issue, user_1: CustomUser) -> IssueComment:
    return fake_comment(issue=issue_1, author=user_1)


@pytest.fixture
def comment_2(issue_1: Issue, user_1: CustomUser) -> IssueComment:
    return fake_comment(issue=issue_1, author=user_1)


@pytest.fixture
def attachment_1(issue_1: Issue) -> IssueAttachment:
    return fake_attachment(issue=issue_1)


@pytest.fixture
def attachment_2(issue_1: Issue, comment_1: IssueComment) -> IssueAttachment:
    return fake_attachment(issue=issue_1, comment=comment_1)
