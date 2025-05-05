import pytest
from django.views import View
from projects.views.project import ProjectCurrentDetailView, ProjectDetailUpdateView, ProjectListCreateView
from rest_framework.test import APIRequestFactory
from tests.utils import check_views_require_authentication

pytestmark = pytest.mark.integration


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name,kwargs,method,view_class",
    [
        ("project-detail-update", {"project_id": 1}, "get", ProjectDetailUpdateView),
        ("project-detail-update", {"project_id": 1}, "put", ProjectDetailUpdateView),
        ("project-list-create", {}, "get", ProjectListCreateView),
        ("project-list-create", {}, "post", ProjectListCreateView),
        ("project-current", {}, "get", ProjectCurrentDetailView),
        ("member-detail-update-delete", {"project_id": 1, "member_id": 1}, "get", ProjectDetailUpdateView),
        ("member-detail-update-delete", {"project_id": 1, "member_id": 1}, "put", ProjectDetailUpdateView),
        ("member-detail-update-delete", {"project_id": 1, "member_id": 1}, "delete", ProjectDetailUpdateView),
        ("member-list-create", {"project_id": 1}, "get", ProjectListCreateView),
        ("member-list-create", {"project_id": 1}, "post", ProjectListCreateView),
    ],
)
def test_project_views_require_authentication(
    url_name: str, kwargs: dict[str, int], method: str, view_class: type[View], request_factory: APIRequestFactory
) -> None:
    check_views_require_authentication(
        url_name=url_name, kwargs=kwargs, method=method, view_class=view_class, request_factory=request_factory
    )
