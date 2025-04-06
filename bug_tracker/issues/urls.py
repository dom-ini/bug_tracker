from django.urls import path
from issues.views.comment import CommentDetailUpdateDeleteView, CommentListCreateView
from issues.views.issue import IssueAssignView, IssueDetailUpdateDeleteView

urlpatterns = [
    path("<int:issue_id>/", IssueDetailUpdateDeleteView.as_view(), name="issue-detail-update-delete"),
    path("<int:issue_id>/assign/", IssueAssignView.as_view(), name="issue-assign"),
    path("<int:issue_id>/comments/", CommentListCreateView.as_view(), name="comment-list-create"),
    path(
        "<int:issue_id>/comments/<int:comment_id>",
        CommentDetailUpdateDeleteView.as_view(),
        name="comment-detail-update-delete",
    ),
]
