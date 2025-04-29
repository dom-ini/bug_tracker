import pytest
from projects.models import Project, ProjectRole
from projects.services import command_member, query_member
from tests.factories import fake_project, fake_user
from users.models import CustomUser

pytestmark = pytest.mark.integration


@pytest.fixture
def user_1() -> CustomUser:
    return fake_user()


@pytest.fixture
def user_2() -> CustomUser:
    return fake_user()


@pytest.fixture
def project_1(user_1: CustomUser) -> Project:
    return fake_project(user=user_1)


@pytest.mark.django_db
def test_member_get_returns_correct_member(project_1: Project, user_1: CustomUser, user_2: CustomUser) -> None:
    command_member.member_add_to_project(
        project=project_1, editor=user_1, email=user_2.email, role=ProjectRole.DEVELOPER
    )

    member = query_member.member_get(project_id=project_1.id, member_id=user_2.id, user=user_1)

    assert member.user_id == user_2.id
    assert member.project_id == project_1.id
    assert member.role == ProjectRole.DEVELOPER


@pytest.mark.django_db
def test_member_get_returns_none_if_requestor_not_part_of_project(
    project_1: Project, user_1: CustomUser, user_2: CustomUser
) -> None:
    member = query_member.member_get(project_id=project_1.id, member_id=user_1.id, user=user_2)

    assert member is None


@pytest.mark.django_db
def test_member_get_returns_none_if_member_not_part_of_project(
    project_1: Project, user_1: CustomUser, user_2: CustomUser
) -> None:
    member = query_member.member_get(project_id=project_1.id, member_id=user_2.id, user=user_1)

    assert member is None


@pytest.mark.django_db
def test_member_get_returns_none_if_invalid_project_id(user_1: CustomUser) -> None:
    member = query_member.member_get(project_id=999, member_id=user_1.id, user=user_1)

    assert member is None


@pytest.mark.django_db
def test_member_list_returns_project_members(project_1: Project, user_1: CustomUser, user_2: CustomUser) -> None:
    command_member.member_add_to_project(
        project=project_1, editor=user_1, email=user_2.email, role=ProjectRole.DEVELOPER
    )

    members = query_member.member_list(project_id=project_1.id, user=user_1)

    member_ids = {(m.user.id, m.role) for m in members}
    assert (user_1.id, ProjectRole.MANAGER) in member_ids
    assert (user_2.id, ProjectRole.DEVELOPER) in member_ids


@pytest.mark.django_db
def test_member_list_returns_empty_if_requestor_not_part_of_project(
    project_1: Project, user_1: CustomUser, user_2: CustomUser
) -> None:
    members = query_member.member_list(project_id=project_1.id, user=user_2)

    assert members.count() == 0


@pytest.mark.django_db
def test_member_list_returns_empty_if_invalid_project_id(project_1: Project, user_1: CustomUser) -> None:
    members = query_member.member_list(project_id=999, user=user_1)

    assert members.count() == 0
