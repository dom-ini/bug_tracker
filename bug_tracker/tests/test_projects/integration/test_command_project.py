import pytest
from django.core.exceptions import ValidationError
from projects.models import Project, ProjectRole, ProjectRoleAssignment
from projects.services import command_member, command_project
from projects.services.exceptions import NotSufficientRoleInProject, SubdomainRecentlyChanged
from pytest_mock import MockerFixture
from tests.factories import fake_project, fake_user
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.fixture
def user_1() -> CustomUser:
    return fake_user()


@pytest.fixture
def project_1(user_1: CustomUser) -> Project:
    return fake_project(user=user_1)


@pytest.mark.django_db
def test_project_create(user_1: CustomUser) -> None:
    project_name = "Test Project"
    project_description = "This is a test project"
    project_subdomain = "test-subdomain"

    project = command_project.project_create(
        name=project_name, description=project_description, subdomain=project_subdomain, user=user_1
    )

    assignment = ProjectRoleAssignment.objects.get(project=project, user=user_1)
    assert project.name == project_name
    assert project.description == project_description
    assert project.subdomain == project_subdomain
    assert assignment.role == ProjectRole.MANAGER


@pytest.mark.django_db
def test_project_create_with_invalid_data(user_1: CustomUser) -> None:
    with pytest.raises(ValidationError):
        command_project.project_create(
            name="Test project", description="Test project", subdomain="invalid with spaces", user=user_1
        )


@pytest.mark.django_db
def test_project_create_description_should_be_cleaned(user_1: CustomUser) -> None:
    malicious_description = "<script>alert('Malicious')</script>safe part of description<p>should not be stripped</p>"

    project = command_project.project_create(
        name="Project", description=malicious_description, subdomain="project-subdomain", user=user_1
    )

    assert project.description == "safe part of description<p>should not be stripped</p>"


@pytest.mark.django_db
def test_project_update_by_manager(user_1: CustomUser, project_1: Project) -> None:
    new_name = "Updated Project Name"
    new_description = "Updated project description"

    project = command_project.project_update(
        project=project_1, editor=user_1, name=new_name, description=new_description
    )

    assert project.name == new_name
    assert project.description == new_description


@pytest.mark.django_db
def test_project_update_by_non_manager_should_fail(user_1: CustomUser, project_1: Project) -> None:
    non_manager = fake_user()
    command_member.member_add_to_project(
        project=project_1, editor=user_1, email=non_manager.email, role=ProjectRole.REPORTER
    )

    with pytest.raises(NotSufficientRoleInProject):
        command_project.project_update(project=project_1, editor=non_manager, name="Invalid Update")


@pytest.mark.django_db
def test_project_update_description_should_be_cleaned(user_1: CustomUser, project_1: Project) -> None:
    malicious_description = "<script>alert('Malicious')</script>safe part of description<p>should not be stripped</p>"

    updated_project = command_project.project_update(
        project=project_1, editor=user_1, description=malicious_description
    )

    assert updated_project.description == "safe part of description<p>should not be stripped</p>"


@pytest.mark.django_db
def test_subdomain_change_not_allowed_before_cooldown(user_1: CustomUser, project_1: Project) -> None:
    new_subdomain = "new-subdomain"

    with pytest.raises(SubdomainRecentlyChanged):
        command_project.project_update(project=project_1, editor=user_1, subdomain=new_subdomain)


@pytest.mark.django_db
def test_subdomain_change_allowed_after_cooldown(user_1: CustomUser, project_1: Project, mocker: MockerFixture) -> None:
    new_subdomain = "new-subdomain"
    mocker.patch("projects.services.command_project._is_subdomain_change_allowed", return_value=(True, ...))

    project = command_project.project_update(project=project_1, editor=user_1, subdomain=new_subdomain)

    assert project.subdomain == new_subdomain
