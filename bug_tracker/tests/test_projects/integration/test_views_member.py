import pytest
from django.urls import reverse
from projects.models import Project, ProjectRole
from projects.services.command_member import member_add_to_project
from projects.views.member import MemberDetailUpdateDeleteView, MemberListCreateView
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from tests.factories import fake_user
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.fixture
def new_member(project: Project) -> CustomUser:
    user = fake_user()
    member_add_to_project(project=project, editor=project.created_by, email=user.email, role=ProjectRole.DEVELOPER)
    return user


@pytest.mark.django_db
def test_member_list_success(
    project: Project, user_with_verified_email: CustomUser, request_factory: APIRequestFactory
) -> None:
    url = reverse("member-list-create", kwargs={"project_id": project.id})

    request = request_factory.get(url)
    force_authenticate(request, user=user_with_verified_email)
    view = MemberListCreateView.as_view()
    response = view(request, project_id=project.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["email"] == user_with_verified_email.email


@pytest.mark.django_db
def test_member_create_success(
    project: Project, user_with_verified_email: CustomUser, request_factory: APIRequestFactory
) -> None:
    url = reverse("member-list-create", kwargs={"project_id": project.id})
    data = {"email": "new@example.com", "role": ProjectRole.DEVELOPER}

    request = request_factory.post(url, data=data)
    force_authenticate(request, user=user_with_verified_email)
    view = MemberListCreateView.as_view()
    response = view(request, project_id=project.id)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_member_create_failure(
    project: Project, user_with_verified_email: CustomUser, request_factory: APIRequestFactory
) -> None:
    url = reverse("member-list-create", kwargs={"project_id": project.id})
    data = {"email": "invalid email", "role": "invalid"}

    request = request_factory.post(url, data=data)
    force_authenticate(request, user=user_with_verified_email)
    view = MemberListCreateView.as_view()
    response = view(request, project_id=project.id)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_member_detail_success(
    project: Project, user_with_verified_email: CustomUser, request_factory: APIRequestFactory
) -> None:
    member_id = user_with_verified_email.id
    url = reverse("member-detail-update-delete", kwargs={"project_id": project.id, "member_id": member_id})

    request = request_factory.get(url)
    force_authenticate(request, user=user_with_verified_email)
    view = MemberDetailUpdateDeleteView.as_view()
    response = view(request, project_id=project.id, member_id=member_id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["email"] == user_with_verified_email.email
    assert response.data["role"] == ProjectRole.MANAGER


@pytest.mark.django_db
def test_member_detail_failure(
    project: Project, user_with_verified_email: CustomUser, request_factory: APIRequestFactory
) -> None:
    url = reverse("member-detail-update-delete", kwargs={"project_id": project.id, "member_id": 999})

    request = request_factory.get(url)
    force_authenticate(request, user=user_with_verified_email)
    view = MemberDetailUpdateDeleteView.as_view()
    response = view(request, project_id=project.id, member_id=999)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_member_update_success(
    project: Project, user_with_verified_email: CustomUser, new_member: CustomUser, request_factory: APIRequestFactory
) -> None:
    url = reverse("member-detail-update-delete", kwargs={"project_id": project.id, "member_id": new_member.id})
    new_role = ProjectRole.REPORTER
    data = {
        "new_role": new_role,
    }

    request = request_factory.put(url, data=data)
    force_authenticate(request, user=user_with_verified_email)
    view = MemberDetailUpdateDeleteView.as_view()
    response = view(request, project_id=project.id, member_id=new_member.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["role"] == new_role


@pytest.mark.django_db
def test_member_update_failure(
    project: Project, user_with_verified_email: CustomUser, request_factory: APIRequestFactory
) -> None:
    member_id = user_with_verified_email.id
    url = reverse("member-detail-update-delete", kwargs={"project_id": project.id, "member_id": member_id})
    data = {
        "new_role": ProjectRole.DEVELOPER,
    }

    request = request_factory.put(url, data=data)
    force_authenticate(request, user=user_with_verified_email)
    view = MemberDetailUpdateDeleteView.as_view()
    response = view(request, project_id=project.id, member_id=member_id)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_member_delete_success(
    project: Project, user_with_verified_email: CustomUser, new_member: CustomUser, request_factory: APIRequestFactory
) -> None:
    member_id = new_member.id
    url = reverse("member-detail-update-delete", kwargs={"project_id": project.id, "member_id": member_id})

    request = request_factory.delete(url)
    force_authenticate(request, user=user_with_verified_email)
    view = MemberDetailUpdateDeleteView.as_view()
    response = view(request, project_id=project.id, member_id=member_id)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_member_delete_failure(
    project: Project, user_with_verified_email: CustomUser, request_factory: APIRequestFactory
) -> None:
    member_id = user_with_verified_email.id
    url = reverse("member-detail-update-delete", kwargs={"project_id": project.id, "member_id": member_id})

    request = request_factory.delete(url)
    force_authenticate(request, user=user_with_verified_email)
    view = MemberDetailUpdateDeleteView.as_view()
    response = view(request, project_id=project.id, member_id=member_id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
