from django.urls import path
from issues.views.attachments import (
    AttachmentDetailDeleteView,
    CommentAttachmentListCreateView,
    IssueAttachmentListCreateView,
)
from issues.views.comment import CommentDetailUpdateDeleteView, CommentListCreateView
from issues.views.history import HistoryListView
from issues.views.issue import IssueAssignView, IssueDetailUpdateDeleteView

urlpatterns = [
    path("<int:issue_id>/", IssueDetailUpdateDeleteView.as_view(), name="issue-detail-update-delete"),
    path("<int:issue_id>/assign/", IssueAssignView.as_view(), name="issue-assign"),
    path("<int:issue_id>/history/", HistoryListView.as_view(), name="issue-history"),
    path("<int:issue_id>/attachments/", IssueAttachmentListCreateView.as_view(), name="issue-attachment-list-create"),
    path("<int:issue_id>/comments/", CommentListCreateView.as_view(), name="comment-list-create"),
    path(
        "<int:issue_id>/comments/<int:comment_id>",
        CommentDetailUpdateDeleteView.as_view(),
        name="comment-detail-update-delete",
    ),
    path(
        "<int:issue_id>/comments/<int:comment_id>/attachments/",
        CommentAttachmentListCreateView.as_view(),
        name="comment-attachment-list-create",
    ),
    path(
        "<int:issue_id>/attachments/<int:attachment_id>",
        AttachmentDetailDeleteView.as_view(),
        name="attachment-detail-delete",
    ),
]
