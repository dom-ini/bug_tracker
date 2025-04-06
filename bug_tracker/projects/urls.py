from django.urls import path
from issues.views.issue import IssueListCreateView
from projects.views.member import MemberDetailUpdateDeleteView, MemberListCreateView
from projects.views.project import ProjectCurrentDetailView, ProjectDetailUpdateView, ProjectListCreateView

urlpatterns = [
    path("", ProjectListCreateView.as_view(), name="project-list-create"),
    path("current/", ProjectCurrentDetailView.as_view(), name="project-current"),
    path("<int:project_id>/", ProjectDetailUpdateView.as_view(), name="project-detail-update"),
    path("<int:project_id>/members/", MemberListCreateView.as_view(), name="member-list-create"),
    path(
        "<int:project_id>/members/<int:member_id>/",
        MemberDetailUpdateDeleteView.as_view(),
        name="member-detail-update-delete",
    ),
    path("<int:project_id>/issues/", IssueListCreateView.as_view(), name="issue-list-create"),
]
