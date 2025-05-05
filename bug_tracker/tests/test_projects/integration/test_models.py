import pytest
from django.core.exceptions import ValidationError
from projects.models import Project, ProjectIdentifier, ProjectRole
from projects.services.command_member import member_add_to_project
from projects.services.query_member import member_get
from tests.factories import fake_user

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_project_subdomain(project: Project) -> None:
    assert project.subdomain == project.identifier.subdomain


@pytest.mark.django_db
def test_project_url(project: Project) -> None:
    url = project.url

    assert url.startswith("https://")
    assert project.subdomain in url


@pytest.mark.django_db
def test_project_str_method(project: Project) -> None:
    assert project.name in str(project)


@pytest.mark.django_db
@pytest.mark.parametrize("subdomain", ["invalid with spaces", "with-invalid-chars-!@#$%^&*()"])
def test_project_identifier_subdomain_validation(subdomain: str) -> None:
    project = Project(name="some project")
    project_identifier = ProjectIdentifier(project=project, subdomain=subdomain)

    with pytest.raises(ValidationError):
        project_identifier.full_clean()


@pytest.mark.django_db
def test_project_identifier_str(project: Project) -> None:
    assert str(project.identifier) == project.identifier.subdomain


@pytest.mark.django_db
def test_project_role_assignment_str(project: Project) -> None:
    user = fake_user()
    role = ProjectRole.DEVELOPER
    member_add_to_project(project=project, editor=project.created_by, email=user.email, role=role)

    assignment = member_get(project_id=project.id, member_id=user.id, user=user)

    assert role in str(assignment)
    assert project.name in str(assignment)
    assert str(user) in str(assignment)
