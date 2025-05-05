import pytest
from django.core.files.base import ContentFile
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse
from issues.models import Issue
from projects.models import Project, ProjectRole
from projects.services import command_member
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import fake_user
from tests.utils import login_as
from users.models import CustomUser

pytestmark = pytest.mark.e2e


@pytest.fixture
def dev_password() -> str:
    return "StrongP@ssword123"


@pytest.fixture
def dev_member(project: Project, dev_password: str) -> CustomUser:
    user = fake_user(password=dev_password)
    command_member.member_add_to_project(
        project=project, editor=project.created_by, email=user.email, role=ProjectRole.DEVELOPER
    )
    return user


@pytest.mark.django_db
def test_issue_management_flow(
    client: APIClient,
    user_with_verified_email: CustomUser,
    password: str,
    dev_member: CustomUser,
    dev_password: str,
    project: Project,
) -> None:
    # login as given project manager
    login_as(client=client, user=user_with_verified_email, password=password)

    # create issue
    issues_url = reverse("issue-list-create", kwargs={"project_id": project.id})
    issue_title = "new issue"
    create_issue_data = {
        "title": issue_title,
        "description": "new issue description",
        "priority": Issue.Priority.CRITICAL,
        "issue_type": Issue.Type.BUG,
        "assigned_to_id": None,
    }
    response = client.post(issues_url, data=create_issue_data)
    assert response.status_code == status.HTTP_201_CREATED

    # new issue should appear in the list
    response = client.get(issues_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["title"] == issue_title

    # edit issue data
    issue_id = response.data["results"][0]["id"]
    issue_details_url = reverse("issue-detail-update-delete", kwargs={"issue_id": issue_id})
    new_description = "description after updating"
    issue_edit_data = {
        "description": new_description,
    }
    response = client.put(issue_details_url, data=issue_edit_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["description"] == new_description

    # assign issue to developer
    issue_assign_url = reverse("issue-assign", kwargs={"issue_id": issue_id})
    issue_assign_data = {
        "assigned_to_id": dev_member.id,
    }
    response = client.put(issue_assign_url, data=issue_assign_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["assigned_to"]["id"] == dev_member.id

    # add comment to issue
    comments_url = reverse("comment-list-create", kwargs={"issue_id": issue_id})
    comment_text = "new comment text"
    comment_create_data = {
        "text": comment_text,
    }
    response = client.post(comments_url, data=comment_create_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["text"] == comment_text
    comment_id = response.data["id"]

    # add attachment to issue
    file_name = "test"
    file_extension = "txt"
    file = ContentFile(b"attachment", name=f"{file_name}.{file_extension}")
    attachment_data = encode_multipart(boundary=BOUNDARY, data={"file": file})
    issue_attachments_url = reverse("issue-attachment-list-create", kwargs={"issue_id": issue_id})
    response = client.post(issue_attachments_url, data=attachment_data, content_type=MULTIPART_CONTENT)
    assert response.status_code == status.HTTP_201_CREATED
    actual_file_name = response.data["url"].split("/")[-1]
    assert actual_file_name.startswith(file_name)
    assert actual_file_name.endswith(file_extension)

    # add attachment to comment
    comment_attachments_url = reverse(
        "comment-attachment-list-create", kwargs={"issue_id": issue_id, "comment_id": comment_id}
    )
    response = client.post(comment_attachments_url, data=attachment_data, content_type=MULTIPART_CONTENT)
    assert response.status_code == status.HTTP_201_CREATED
    actual_file_name = response.data["url"].split("/")[-1]
    assert actual_file_name.startswith(file_name)
    assert actual_file_name.endswith(file_extension)

    # login as developer
    login_as(client=client, user=dev_member, password=dev_password)

    # get assigned issues list
    response = client.get(issues_url, data={"assigned_to": dev_member.id})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["title"] == issue_title

    # try to edit issue data - should fail
    issue_edit_data = {
        "description": "some description",
    }
    response = client.put(issue_details_url, data=issue_edit_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
