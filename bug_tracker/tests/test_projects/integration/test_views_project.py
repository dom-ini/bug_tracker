import pytest
from django.conf import settings
from django.urls import reverse
from django.views import View
from projects.models import Project
from projects.views.project import ProjectCurrentDetailView, ProjectDetailUpdateView, ProjectListCreateView
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_project_detail_success(
    project: Project, user_with_verified_email: CustomUser, request_factory: APIRequestFactory
) -> None:
    url = reverse("project-detail-update", kwargs={"project_id": project.id})

    request = request_factory.get(url)
    force_authenticate(request, user=user_with_verified_email)
    view = ProjectDetailUpdateView.as_view()
    response = view(request, project_id=project.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == project.name


@pytest.mark.django_db
def test_project_detail_failure(user_with_verified_email: CustomUser, request_factory: APIRequestFactory) -> None:
    project_id = 999
    url = reverse("project-detail-update", kwargs={"project_id": project_id})

    request = request_factory.get(url)
    force_authenticate(request, user=user_with_verified_email)
    view = ProjectDetailUpdateView.as_view()
    response = view(request, project_id=project_id)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_project_update_success(
    project: Project, user_with_verified_email: CustomUser, request_factory: APIRequestFactory
) -> None:
    url = reverse("project-detail-update", kwargs={"project_id": project.id})
    new_name = "new project name"
    data = {
        "name": new_name,
    }

    request = request_factory.put(url, data=data)
    force_authenticate(request, user=user_with_verified_email)
    view = ProjectDetailUpdateView.as_view()
    response = view(request, project_id=project.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == new_name


@pytest.mark.django_db
def test_project_update_failure(
    project: Project, user_with_verified_email: CustomUser, request_factory: APIRequestFactory
) -> None:
    url = reverse("project-detail-update", kwargs={"project_id": project.id})
    data = {
        "subdomain": "inv@lid subdomain",
    }

    request = request_factory.put(url, data=data)
    force_authenticate(request, user=user_with_verified_email)
    view = ProjectDetailUpdateView.as_view()
    response = view(request, project_id=project.id)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.django_db
def test_project_list_success(
    project: Project, user_with_verified_email: CustomUser, request_factory: APIRequestFactory
) -> None:
    url = reverse("project-list-create")

    request = request_factory.get(url)
    force_authenticate(request, user=user_with_verified_email)
    view = ProjectListCreateView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == project.name


@pytest.mark.django_db
def test_project_create_success(user_with_verified_email: CustomUser, request_factory: APIRequestFactory) -> None:
    url = reverse("project-list-create")
    data = {
        "name": "new project name",
        "description": "new project description",
        "subdomain": "new-project-subdomain",
    }

    request = request_factory.post(url, data=data)
    force_authenticate(request, user=user_with_verified_email)
    view = ProjectListCreateView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_project_create_failure(user_with_verified_email: CustomUser, request_factory: APIRequestFactory) -> None:
    url = reverse("project-list-create")
    data = {
        "name": "new project name",
        "description": "new project description",
        "subdomain": "inv@lid subdomain",
    }

    request = request_factory.post(url, data=data)
    force_authenticate(request, user=user_with_verified_email)
    view = ProjectListCreateView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_project_current_detail_success(
    project: Project, user_with_verified_email: CustomUser, request_factory: APIRequestFactory
) -> None:
    url = reverse("project-current")

    request = request_factory.get(url, headers={settings.SUBDOMAIN_HEADER_NAME: project.subdomain})
    force_authenticate(request, user=user_with_verified_email)
    view = ProjectCurrentDetailView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == project.name


@pytest.mark.django_db
def test_project_current_detail_failure(
    project: Project, user_with_verified_email: CustomUser, request_factory: APIRequestFactory
) -> None:
    url = reverse("project-current")

    request = request_factory.get(url, headers={settings.SUBDOMAIN_HEADER_NAME: "invalid-subdomain"})
    force_authenticate(request, user=user_with_verified_email)
    view = ProjectCurrentDetailView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name,kwargs,method,view_class",
    [
        ("project-detail-update", {"project_id": 1}, "get", ProjectDetailUpdateView),
        ("project-detail-update", {"project_id": 1}, "put", ProjectDetailUpdateView),
        ("project-list-create", {}, "get", ProjectListCreateView),
        ("project-list-create", {}, "post", ProjectListCreateView),
        ("project-current", {}, "get", ProjectCurrentDetailView),
    ],
)
def test_project_views_require_authentication(
    url_name: str, kwargs: dict[str, int], method: str, view_class: type[View], request_factory: APIRequestFactory
) -> None:
    url = reverse(url_name, kwargs=kwargs)

    request = getattr(request_factory, method)(url)
    response = view_class.as_view()(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
