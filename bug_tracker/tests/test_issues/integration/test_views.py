import pytest
from django.views import View
from issues.views.attachment import (
    AttachmentDetailDeleteView,
    CommentAttachmentListCreateView,
    IssueAttachmentListCreateView,
)
from issues.views.comment import CommentDetailUpdateDeleteView, CommentListCreateView
from issues.views.history import HistoryListView
from issues.views.issue import IssueAssignView, IssueDetailUpdateDeleteView, IssueListCreateView
from rest_framework.test import APIRequestFactory
from tests.utils import check_views_require_authentication

pytestmark = pytest.mark.integration


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name,kwargs,method,view_class",
    [
        ("issue-list-create", {"project_id": 1}, "get", IssueListCreateView),
        ("issue-list-create", {"project_id": 1}, "post", IssueListCreateView),
        ("issue-detail-update-delete", {"issue_id": 1}, "get", IssueDetailUpdateDeleteView),
        ("issue-detail-update-delete", {"issue_id": 1}, "put", IssueDetailUpdateDeleteView),
        ("issue-detail-update-delete", {"issue_id": 1}, "delete", IssueDetailUpdateDeleteView),
        ("issue-assign", {"issue_id": 1}, "put", IssueAssignView),
        ("issue-history", {"issue_id": 1}, "get", HistoryListView),
        ("comment-list-create", {"issue_id": 1}, "get", CommentListCreateView),
        ("comment-list-create", {"issue_id": 1}, "post", CommentListCreateView),
        ("comment-detail-update-delete", {"issue_id": 1, "comment_id": 1}, "get", CommentDetailUpdateDeleteView),
        ("comment-detail-update-delete", {"issue_id": 1, "comment_id": 1}, "put", CommentDetailUpdateDeleteView),
        ("comment-detail-update-delete", {"issue_id": 1, "comment_id": 1}, "delete", CommentDetailUpdateDeleteView),
        ("attachment-detail-delete", {"issue_id": 1, "attachment_id": 1}, "get", AttachmentDetailDeleteView),
        ("attachment-detail-delete", {"issue_id": 1, "attachment_id": 1}, "delete", AttachmentDetailDeleteView),
        ("issue-attachment-list-create", {"issue_id": 1}, "get", IssueAttachmentListCreateView),
        ("issue-attachment-list-create", {"issue_id": 1}, "post", IssueAttachmentListCreateView),
        ("comment-attachment-list-create", {"issue_id": 1, "comment_id": 1}, "get", CommentAttachmentListCreateView),
        ("comment-attachment-list-create", {"issue_id": 1, "comment_id": 1}, "post", CommentAttachmentListCreateView),
    ],
)
def test_issue_views_require_authentication(
    url_name: str, kwargs: dict[str, int], method: str, view_class: type[View], request_factory: APIRequestFactory
) -> None:
    check_views_require_authentication(
        url_name=url_name, kwargs=kwargs, method=method, view_class=view_class, request_factory=request_factory
    )
