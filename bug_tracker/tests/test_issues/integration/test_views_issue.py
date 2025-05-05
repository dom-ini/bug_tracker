import pytest
from django.urls import reverse
from issues.models import Issue
from issues.views.issue import IssueAssignView, IssueDetailUpdateDeleteView, IssueListCreateView
from projects.models import Project
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_issue_detail_success(request_factory: APIRequestFactory, issue_1: Issue, user_1: CustomUser) -> None:
    url = reverse("issue-detail-update-delete", kwargs={"issue_id": issue_1.id})

    request = request_factory.get(url)
    force_authenticate(request, user=user_1)
    view = IssueDetailUpdateDeleteView.as_view()
    response = view(request, issue_id=issue_1.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == issue_1.title


@pytest.mark.django_db
def test_issue_detail_failure(request_factory: APIRequestFactory, user_1: CustomUser) -> None:
    issue_id = 999
    url = reverse("issue-detail-update-delete", kwargs={"issue_id": issue_id})

    request = request_factory.get(url)
    force_authenticate(request, user=user_1)
    view = IssueDetailUpdateDeleteView.as_view()
    response = view(request, issue_id=issue_id)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_issue_update_success(request_factory: APIRequestFactory, user_1: CustomUser, issue_1: Issue) -> None:
    url = reverse("issue-detail-update-delete", kwargs={"issue_id": issue_1.id})
    new_title = "new issue title"
    data = {
        "title": new_title,
    }

    request = request_factory.put(url, data=data)
    force_authenticate(request, user=user_1)
    view = IssueDetailUpdateDeleteView.as_view()
    response = view(request, issue_id=issue_1.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == new_title


@pytest.mark.django_db
def test_issue_update_failure(request_factory: APIRequestFactory, user_1: CustomUser, issue_1: Issue) -> None:
    url = reverse("issue-detail-update-delete", kwargs={"issue_id": issue_1.id})
    data = {
        "priority": "invalid",
    }

    request = request_factory.put(url, data=data)
    force_authenticate(request, user=user_1)
    view = IssueDetailUpdateDeleteView.as_view()
    response = view(request, issue_id=issue_1.id)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_issue_delete_success(request_factory: APIRequestFactory, user_1: CustomUser, issue_1: Issue) -> None:
    url = reverse("issue-detail-update-delete", kwargs={"issue_id": issue_1.id})

    request = request_factory.delete(url)
    force_authenticate(request, user=user_1)
    view = IssueDetailUpdateDeleteView.as_view()
    response = view(request, issue_id=issue_1.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_issue_delete_failure(request_factory: APIRequestFactory, user_1: CustomUser, issue_1: Issue) -> None:
    url = reverse("issue-detail-update-delete", kwargs={"issue_id": 999})

    request = request_factory.delete(url)
    force_authenticate(request, user=user_1)
    view = IssueDetailUpdateDeleteView.as_view()
    response = view(request, issue_id=999)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_issue_list_success(issue_1: Issue, user_1: CustomUser, request_factory: APIRequestFactory) -> None:
    url = reverse("issue-list-create", kwargs={"project_id": issue_1.project.id})

    request = request_factory.get(url)
    force_authenticate(request, user=user_1)
    view = IssueListCreateView.as_view()
    response = view(request, project_id=issue_1.project.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["title"] == issue_1.title


@pytest.mark.django_db
def test_issue_list_failure(issue_1: Issue, user_1: CustomUser, request_factory: APIRequestFactory) -> None:
    url = reverse("issue-list-create", kwargs={"project_id": issue_1.project.id})

    request = request_factory.get(url, data={"status": "invalid"})
    force_authenticate(request, user=user_1)
    view = IssueListCreateView.as_view()
    response = view(request, project_id=issue_1.project.id)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_issue_create_success(user_1: CustomUser, project_1: Project, request_factory: APIRequestFactory) -> None:
    url = reverse("issue-list-create", kwargs={"project_id": project_1.id})
    data = {
        "title": "new issue title",
        "description": "new issue description",
        "priority": Issue.Priority.MEDIUM,
        "issue_type": Issue.Type.BUG,
        "assigned_to_id": None,
    }

    request = request_factory.post(url, data=data)
    force_authenticate(request, user=user_1)
    view = IssueListCreateView.as_view()
    response = view(request, project_id=project_1.id)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_issue_create_failure(user_1: CustomUser, project_1: Project, request_factory: APIRequestFactory) -> None:
    url = reverse("issue-list-create", kwargs={"project_id": project_1.id})
    data = {
        "title": "new issue title",
        "description": "new issue description",
        "priority": "invalid",
        "issue_type": "invalid",
        "assigned_to_id": None,
    }

    request = request_factory.post(url, data=data)
    force_authenticate(request, user=user_1)
    view = IssueListCreateView.as_view()
    response = view(request, project_id=project_1.id)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_issue_assign_success(request_factory: APIRequestFactory, user_1: CustomUser, issue_1: Issue) -> None:
    url = reverse("issue-assign", kwargs={"issue_id": issue_1.id})
    data = {
        "assigned_to_id": user_1.id,
    }

    request = request_factory.put(url, data=data)
    force_authenticate(request, user=user_1)
    view = IssueAssignView.as_view()
    response = view(request, issue_id=issue_1.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["assigned_to"]["id"] == user_1.id


@pytest.mark.django_db
def test_issue_assign_failure(request_factory: APIRequestFactory, user_1: CustomUser, issue_1: Issue) -> None:
    url = reverse("issue-assign", kwargs={"issue_id": issue_1.id})
    data = {
        "assigned_to_id": "invalid",
    }

    request = request_factory.put(url, data=data)
    force_authenticate(request, user=user_1)
    view = IssueAssignView.as_view()
    response = view(request, issue_id=issue_1.id)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
