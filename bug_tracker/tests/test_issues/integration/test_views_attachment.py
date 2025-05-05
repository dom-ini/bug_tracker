import pytest
from django.core.files.base import ContentFile
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse
from issues.models import Issue, IssueAttachment, IssueComment
from issues.views.attachment import (
    AttachmentDetailDeleteView,
    CommentAttachmentListCreateView,
    IssueAttachmentListCreateView,
)
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_attachment_detail_success(
    request_factory: APIRequestFactory, attachment_1: IssueAttachment, user_1: CustomUser
) -> None:
    url = reverse(
        "attachment-detail-delete", kwargs={"issue_id": attachment_1.issue.id, "attachment_id": attachment_1.id}
    )

    request = request_factory.get(url)
    force_authenticate(request, user=user_1)
    view = AttachmentDetailDeleteView.as_view()
    response = view(request, issue_id=attachment_1.issue.id, attachment_id=attachment_1.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["url"] == attachment_1.url


@pytest.mark.django_db
def test_attachment_detail_failure(request_factory: APIRequestFactory, issue_1: Issue, user_1: CustomUser) -> None:
    attachment_id = 999
    url = reverse("attachment-detail-delete", kwargs={"issue_id": issue_1.id, "attachment_id": attachment_id})

    request = request_factory.get(url)
    force_authenticate(request, user=user_1)
    view = AttachmentDetailDeleteView.as_view()
    response = view(request, issue_id=issue_1.id, attachment_id=attachment_id)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_attachment_delete_success(
    request_factory: APIRequestFactory, user_1: CustomUser, attachment_1: IssueAttachment
) -> None:
    url = reverse(
        "attachment-detail-delete", kwargs={"issue_id": attachment_1.issue.id, "attachment_id": attachment_1.id}
    )

    request = request_factory.delete(url)
    force_authenticate(request, user=user_1)
    view = AttachmentDetailDeleteView.as_view()
    response = view(request, issue_id=attachment_1.issue.id, attachment_id=attachment_1.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_attachment_delete_failure(
    request_factory: APIRequestFactory, user_1: CustomUser, attachment_1: IssueAttachment
) -> None:
    url = reverse("attachment-detail-delete", kwargs={"issue_id": attachment_1.issue.id, "attachment_id": 999})

    request = request_factory.delete(url)
    force_authenticate(request, user=user_1)
    view = AttachmentDetailDeleteView.as_view()
    response = view(request, issue_id=attachment_1.issue.id, attachment_id=999)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_comment_attachment_list_success(
    attachment_2: IssueAttachment, user_1: CustomUser, request_factory: APIRequestFactory
) -> None:
    url = reverse(
        "comment-attachment-list-create",
        kwargs={"issue_id": attachment_2.issue.id, "comment_id": attachment_2.comment.id},
    )

    request = request_factory.get(url)
    force_authenticate(request, user=user_1)
    view = CommentAttachmentListCreateView.as_view()
    response = view(request, issue_id=attachment_2.issue.id, comment_id=attachment_2.comment.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["url"] == attachment_2.url


@pytest.mark.django_db
def test_comment_attachment_create_success(
    user_1: CustomUser, comment_1: IssueComment, request_factory: APIRequestFactory
) -> None:
    url = reverse("comment-attachment-list-create", kwargs={"issue_id": comment_1.issue.id, "comment_id": comment_1.id})
    file = ContentFile(b"content", "test.txt")
    data = encode_multipart(
        boundary=BOUNDARY,
        data={
            "file": file,
        },
    )

    request = request_factory.post(url, data=data, content_type=MULTIPART_CONTENT)
    force_authenticate(request, user=user_1)
    view = CommentAttachmentListCreateView.as_view()
    response = view(request, issue_id=comment_1.issue.id, comment_id=comment_1.id)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_comment_attachment_create_failure(
    user_1: CustomUser, comment_1: IssueComment, request_factory: APIRequestFactory
) -> None:
    url = reverse("comment-attachment-list-create", kwargs={"issue_id": comment_1.issue.id, "comment_id": comment_1.id})
    file = ContentFile(b"content", "invalid.ini")
    data = {
        "file": file,
    }

    request = request_factory.post(url, data=data, content_type="multipart/form-data")
    force_authenticate(request, user=user_1)
    view = CommentAttachmentListCreateView.as_view()
    response = view(request, issue_id=comment_1.issue.id, comment_id=comment_1.id)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_issue_attachment_list_success(
    attachment_1: IssueAttachment, user_1: CustomUser, request_factory: APIRequestFactory
) -> None:
    url = reverse("issue-attachment-list-create", kwargs={"issue_id": attachment_1.issue.id})

    request = request_factory.get(url)
    force_authenticate(request, user=user_1)
    view = IssueAttachmentListCreateView.as_view()
    response = view(request, issue_id=attachment_1.issue.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["url"] == attachment_1.url


@pytest.mark.django_db
def test_issue_attachment_create_success(
    user_1: CustomUser, issue_1: Issue, request_factory: APIRequestFactory
) -> None:
    url = reverse("issue-attachment-list-create", kwargs={"issue_id": issue_1.id})
    file = ContentFile(b"content", "test.txt")
    data = encode_multipart(
        boundary=BOUNDARY,
        data={
            "file": file,
        },
    )

    request = request_factory.post(url, data=data, content_type=MULTIPART_CONTENT)
    force_authenticate(request, user=user_1)
    view = IssueAttachmentListCreateView.as_view()
    response = view(request, issue_id=issue_1.id)

    print(response.data)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_issue_attachment_create_failure(
    user_1: CustomUser, issue_1: Issue, request_factory: APIRequestFactory
) -> None:
    url = reverse("issue-attachment-list-create", kwargs={"issue_id": issue_1.id})
    file = ContentFile(b"content", "invalid.ini")
    data = {
        "file": file,
    }

    request = request_factory.post(url, data=data, content_type="multipart/form-data")
    force_authenticate(request, user=user_1)
    view = IssueAttachmentListCreateView.as_view()
    response = view(request, issue_id=issue_1.id)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
