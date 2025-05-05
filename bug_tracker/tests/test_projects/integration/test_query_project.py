from typing import Sequence

import pytest
from projects.models import ProjectRole
from projects.services import command_member, query_project
from tests.factories import fake_project, fake_user

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_project_get_returns_project_with_user_role() -> None:
    user = fake_user()
    project = fake_project(user=user)

    fetched_project = query_project.project_get(project_id=project.id, user=user)

    assert fetched_project is not None
    assert fetched_project.id == project.id
    assert fetched_project.role == ProjectRole.MANAGER


@pytest.mark.django_db
def test_project_get_returns_none_if_not_member() -> None:
    user_member = fake_user()
    user_not_member = fake_user()
    project = fake_project(user=user_member)

    fetched_project = query_project.project_get(project_id=project.id, user=user_not_member)

    assert fetched_project is None


@pytest.mark.django_db
def test_project_get_returns_none_if_invalid_project_id() -> None:
    user_member = fake_user()

    fetched_project = query_project.project_get(project_id=999, user=user_member)

    assert fetched_project is None


@pytest.mark.django_db
def test_project_get_by_subdomain_returns_project_with_user_role() -> None:
    user = fake_user()
    project = fake_project(user=user)

    fetched_project = query_project.project_get_by_subdomain(subdomain=project.subdomain, user=user)

    assert fetched_project is not None
    assert fetched_project.id == project.id
    assert fetched_project.role == ProjectRole.MANAGER


@pytest.mark.django_db
def test_project_get_by_subdomain_returns_none_if_not_member() -> None:
    user_member = fake_user()
    user_not_member = fake_user()
    project = fake_project(user=user_member)

    fetched_project = query_project.project_get_by_subdomain(subdomain=project.subdomain, user=user_not_member)

    assert fetched_project is None


@pytest.mark.django_db
def test_project_list_filters_projects_for_user() -> None:
    user_1 = fake_user()
    project_1 = fake_project(user=user_1)
    project_2 = fake_project(user=user_1)
    user_2 = fake_user()
    fake_project(user=user_2)

    projects = query_project.project_list(user=user_1)

    project_ids = {p.id for p in projects}
    assert project_1.id in project_ids
    assert project_2.id in project_ids
    assert len(projects) == 2


@pytest.mark.django_db
def test_project_get_user_role_returns_correct_role() -> None:
    user_mng = fake_user()
    user_dev = fake_user()
    project = fake_project(user=user_mng)
    command_member.member_add_to_project(
        project=project, editor=user_mng, email=user_dev.email, role=ProjectRole.DEVELOPER
    )

    role_1 = query_project.project_get_user_role(project=project, user=user_mng)
    role_2 = query_project.project_get_user_role(project=project, user=user_dev)

    assert role_1 == ProjectRole.MANAGER
    assert role_2 == ProjectRole.DEVELOPER


@pytest.mark.django_db
def test_project_get_user_role_returns_none_if_not_assigned() -> None:
    user_member = fake_user()
    user_not_member = fake_user()
    project = fake_project(user=user_member)

    role = query_project.project_get_user_role(project=project, user=user_not_member)

    assert role is None


@pytest.mark.django_db
@pytest.mark.parametrize("roles,expected", [([ProjectRole.MANAGER], True), ([ProjectRole.DEVELOPER], False)])
def test_project_has_user_roles_returns_true_for_correct_role(roles: Sequence[ProjectRole], expected: bool) -> None:
    user = fake_user()
    project = fake_project(user=user)

    has_role = query_project.project_has_user_roles(project=project, user=user, roles=roles)

    assert has_role is expected


@pytest.mark.django_db
def test_project_has_user_roles_returns_false_if_not_a_member() -> None:
    user_member = fake_user()
    user_not_member = fake_user()
    project = fake_project(user=user_member)

    has_role = query_project.project_has_user_roles(project=project, user=user_not_member, roles=[ProjectRole.MANAGER])

    assert has_role is False
