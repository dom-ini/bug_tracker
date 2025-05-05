import pytest
from django.urls import reverse
from issues.models import Issue, IssueComment
from issues.views.history import HistoryListView
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_history_list_success(
    request_factory: APIRequestFactory,
    user_1: CustomUser,
    issue_1: Issue,
    comment_1: IssueComment,
    comment_2: IssueComment,
) -> None:
    url = reverse("issue-history", kwargs={"issue_id": issue_1.id})

    request = request_factory.get(url)
    force_authenticate(request, user=user_1)
    view = HistoryListView.as_view()
    response = view(request, issue_id=issue_1.id)

    assert response.status_code == status.HTTP_200_OK
    # 1 issue creation and 2 comments creation
    assert response.data["count"] == 3


@pytest.mark.django_db
def test_history_list_failure(request_factory: APIRequestFactory, user_1: CustomUser, issue_1: Issue) -> None:
    url = reverse("issue-history", kwargs={"issue_id": issue_1.id})

    request = request_factory.get(url, data={"content_type": "invalid"})
    force_authenticate(request, user=user_1)
    view = HistoryListView.as_view()
    response = view(request, issue_id=issue_1.id)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
