import pytest
from issues.models import Issue, IssueAttachment
from projects.models import Project
from tests.factories import fake_attachment, fake_issue


@pytest.fixture
def issue(project: Project) -> Issue:
    return fake_issue(project=project, user=project.created_by)


@pytest.fixture
def attachment(issue: Issue) -> IssueAttachment:
    return fake_attachment(issue=issue)
