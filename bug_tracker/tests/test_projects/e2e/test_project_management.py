import pytest
from django.conf import settings
from django.core import mail
from django.urls import reverse
from projects.models import ProjectRole
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import fake_user
from users.models import CustomUser

pytestmark = pytest.mark.e2e


@pytest.mark.django_db
def test_project_management_flow(client: APIClient, user_with_verified_email: CustomUser, password: str) -> None:
    # try to access projects unauthenticated
    projects_url = reverse("project-list-create")
    response = client.get(projects_url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # login as (future) manager
    login_url = reverse("rest_login")
    login_data = {
        "username": user_with_verified_email.username,
        "password": password,
    }
    response = client.post(login_url, data=login_data)
    assert response.status_code == status.HTTP_200_OK, "Manager login failed"
    token = response.data["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # access projects list
    response = client.get(projects_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0

    # create project
    project_name = "new project"
    project_subdomain = "project-subdomain"
    create_project_data = {
        "name": project_name,
        "description": "new project description",
        "subdomain": project_subdomain,
    }
    response = client.post(projects_url, data=create_project_data)
    assert response.status_code == status.HTTP_201_CREATED

    # new project should appear in the list
    response = client.get(projects_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == project_name

    # get current project details
    current_project_url = reverse("project-current")
    response = client.get(current_project_url, headers={settings.SUBDOMAIN_HEADER_NAME: project_subdomain})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == project_name
    assert response.data["role"] == ProjectRole.MANAGER

    # edit project data
    project_id = response.data["id"]
    project_details_url = reverse("project-detail-update", kwargs={"project_id": project_id})
    new_description = "description after updating"
    project_edit_data = {
        "description": new_description,
    }
    response = client.put(project_details_url, data=project_edit_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["description"] == new_description

    # add new member (developer)
    members_url = reverse("member-list-create", kwargs={"project_id": project_id})
    dev_password = "StrongP@ssword123"
    dev_user = fake_user(password=dev_password)
    new_member_data = {
        "email": dev_user.email,
        "role": ProjectRole.DEVELOPER,
    }
    assert len(mail.outbox) == 0
    response = client.post(members_url, data=new_member_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert len(mail.outbox) == 1
    invitation_email = mail.outbox[0]
    assert dev_user.email in invitation_email.to

    # login as developer
    login_data = {
        "username": dev_user.username,
        "password": dev_password,
    }
    response = client.post(login_url, data=login_data)
    assert response.status_code == status.HTTP_200_OK, "Developer login failed"
    token = response.data["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # project should be in the list
    response = client.get(projects_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == project_name
    assert response.data["results"][0]["role"] == ProjectRole.DEVELOPER

    # try to edit project data - should fail
    project_edit_data = {
        "description": "new description",
    }
    response = client.put(project_details_url, data=project_edit_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
