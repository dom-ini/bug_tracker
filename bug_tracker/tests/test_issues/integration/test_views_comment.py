import pytest
from django.urls import reverse
from issues.models import Issue, IssueComment
from issues.views.comment import CommentDetailUpdateDeleteView, CommentListCreateView
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_comment_detail_success(
    request_factory: APIRequestFactory, comment_1: IssueComment, user_1: CustomUser
) -> None:
    url = reverse("comment-detail-update-delete", kwargs={"issue_id": comment_1.issue.id, "comment_id": comment_1.id})

    request = request_factory.get(url)
    force_authenticate(request, user=user_1)
    view = CommentDetailUpdateDeleteView.as_view()
    response = view(request, issue_id=comment_1.issue.id, comment_id=comment_1.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["text"] == comment_1.text


@pytest.mark.django_db
def test_comment_detail_failure(request_factory: APIRequestFactory, issue_1: Issue, user_1: CustomUser) -> None:
    comment_id = 999
    url = reverse("comment-detail-update-delete", kwargs={"issue_id": issue_1.id, "comment_id": comment_id})

    request = request_factory.get(url)
    force_authenticate(request, user=user_1)
    view = CommentDetailUpdateDeleteView.as_view()
    response = view(request, issue_id=issue_1.id, comment_id=comment_id)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_comment_update_success(
    request_factory: APIRequestFactory, user_1: CustomUser, comment_1: IssueComment
) -> None:
    url = reverse("comment-detail-update-delete", kwargs={"issue_id": comment_1.issue.id, "comment_id": comment_1.id})
    new_text = "new comment content"
    data = {
        "text": new_text,
    }

    request = request_factory.put(url, data=data)
    force_authenticate(request, user=user_1)
    view = CommentDetailUpdateDeleteView.as_view()
    response = view(request, issue_id=comment_1.issue.id, comment_id=comment_1.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["text"] == new_text


@pytest.mark.django_db
def test_comment_update_failure(
    request_factory: APIRequestFactory, user_1: CustomUser, comment_1: IssueComment
) -> None:
    url = reverse("comment-detail-update-delete", kwargs={"issue_id": 999, "comment_id": comment_1.id})
    data = {
        "text": "some text",
    }

    request = request_factory.put(url, data=data)
    force_authenticate(request, user=user_1)
    view = CommentDetailUpdateDeleteView.as_view()
    response = view(request, issue_id=999, comment_id=comment_1.id)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_comment_delete_success(
    request_factory: APIRequestFactory, user_1: CustomUser, comment_1: IssueComment
) -> None:
    url = reverse("comment-detail-update-delete", kwargs={"issue_id": comment_1.issue.id, "comment_id": comment_1.id})

    request = request_factory.delete(url)
    force_authenticate(request, user=user_1)
    view = CommentDetailUpdateDeleteView.as_view()
    response = view(request, issue_id=comment_1.issue.id, comment_id=comment_1.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_comment_delete_failure(
    request_factory: APIRequestFactory, user_1: CustomUser, comment_1: IssueComment
) -> None:
    url = reverse("comment-detail-update-delete", kwargs={"issue_id": comment_1.issue.id, "comment_id": 999})

    request = request_factory.delete(url)
    force_authenticate(request, user=user_1)
    view = CommentDetailUpdateDeleteView.as_view()
    response = view(request, issue_id=comment_1.issue.id, comment_id=999)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_comment_list_success(comment_1: IssueComment, user_1: CustomUser, request_factory: APIRequestFactory) -> None:
    url = reverse("comment-list-create", kwargs={"issue_id": comment_1.issue.id})

    request = request_factory.get(url)
    force_authenticate(request, user=user_1)
    view = CommentListCreateView.as_view()
    response = view(request, issue_id=comment_1.issue.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["text"] == comment_1.text


@pytest.mark.django_db
def test_comment_list_failure(comment_1: IssueComment, user_1: CustomUser, request_factory: APIRequestFactory) -> None:
    url = reverse("comment-list-create", kwargs={"issue_id": comment_1.issue.id})

    request = request_factory.get(url, data={"author": "invalid"})
    force_authenticate(request, user=user_1)
    view = CommentListCreateView.as_view()
    response = view(request, issue_id=comment_1.issue.id)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_comment_create_success(user_1: CustomUser, issue_1: Issue, request_factory: APIRequestFactory) -> None:
    url = reverse("comment-list-create", kwargs={"issue_id": issue_1.id})
    data = {
        "text": "new comment content",
    }

    request = request_factory.post(url, data=data)
    force_authenticate(request, user=user_1)
    view = CommentListCreateView.as_view()
    response = view(request, issue_id=issue_1.id)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_comment_create_failure(user_1: CustomUser, issue_1: Issue, request_factory: APIRequestFactory) -> None:
    url = reverse("comment-list-create", kwargs={"issue_id": 999})
    data = {
        "text": "new comment text",
    }

    request = request_factory.post(url, data=data)
    force_authenticate(request, user=user_1)
    view = CommentListCreateView.as_view()
    response = view(request, issue_id=999)

    assert response.status_code == status.HTTP_404_NOT_FOUND
