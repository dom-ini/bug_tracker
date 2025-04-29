import pytest
from projects.models import Project, ProjectRole
from projects.services import command_member, query_member
from projects.services.exceptions import (
    MemberAlreadyInProject,
    NotSufficientRoleInProject,
    UserCannotModifyOwnMembership,
)
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
def test_member_add_to_project(project_1: Project, user_1: CustomUser) -> None:
    member = command_member.member_add_to_project(
        project=project_1, editor=user_1, email="new@example.com", role=ProjectRole.REPORTER
    )

    assert member.role == ProjectRole.REPORTER
    assert member.project_id == project_1.id


@pytest.mark.django_db
def test_member_add_to_project_by_non_manager_should_fail(project_1: Project, user_2: CustomUser) -> None:
    with pytest.raises(NotSufficientRoleInProject):
        command_member.member_add_to_project(
            project=project_1, editor=user_2, email="new@example.com", role=ProjectRole.REPORTER
        )


@pytest.mark.django_db
def test_member_add_to_project_member_already_in_project_should_fail(
    project_1: Project, user_1: CustomUser, user_2: CustomUser
) -> None:
    command_member.member_add_to_project(
        project=project_1, editor=user_1, email=user_2.email, role=ProjectRole.REPORTER
    )

    with pytest.raises(MemberAlreadyInProject):
        command_member.member_add_to_project(
            project=project_1, editor=user_1, email=user_2.email, role=ProjectRole.DEVELOPER
        )


@pytest.mark.django_db
def test_member_change_role_in_project(project_1: Project, user_1: CustomUser, user_2: CustomUser) -> None:
    old_role = ProjectRole.REPORTER
    new_role = ProjectRole.DEVELOPER
    member = command_member.member_add_to_project(project=project_1, editor=user_1, email=user_2.email, role=old_role)

    updated_member = command_member.member_change_role_in_project(
        project=project_1, editor=user_1, member=member, new_role=new_role
    )

    assert updated_member.role == new_role


@pytest.mark.django_db
def test_member_change_role_in_project_by_non_manager_should_fail(
    project_1: Project, user_1: CustomUser, user_2: CustomUser
) -> None:
    command_member.member_add_to_project(
        project=project_1, editor=user_1, email=user_2.email, role=ProjectRole.DEVELOPER
    )
    member = query_member.member_get(project_id=project_1.id, member_id=user_1.id, user=user_2)

    with pytest.raises(NotSufficientRoleInProject):
        command_member.member_change_role_in_project(
            project=project_1, editor=user_2, member=member, new_role=ProjectRole.DEVELOPER
        )


@pytest.mark.django_db
def test_member_change_role_in_project_self_membership_should_fail(
    project_1: Project, user_1: CustomUser, user_2: CustomUser
) -> None:
    member = command_member.member_add_to_project(
        project=project_1, editor=user_1, email=user_2.email, role=ProjectRole.MANAGER
    )

    with pytest.raises(UserCannotModifyOwnMembership):
        command_member.member_change_role_in_project(
            project=project_1, editor=user_2, member=member, new_role=ProjectRole.REPORTER
        )


@pytest.mark.django_db
def test_member_remove_from_project(project_1: Project, user_1: CustomUser, user_2: CustomUser) -> None:
    command_member.member_add_to_project(project=project_1, editor=user_1, email=user_2.email, role=ProjectRole.MANAGER)
    member = query_member.member_get(project_id=project_1.id, member_id=user_1.id, user=user_2)

    command_member.member_remove_from_project(project=project_1, editor=user_2, member=member)

    members = query_member.member_list(project_id=project_1.id, user=user_2)
    members_ids = {m.user.id for m in members}
    assert user_1.id not in members_ids
    assert user_2.id in members_ids


@pytest.mark.django_db
def test_member_remove_from_project_by_non_manager_should_fail(
    project_1: Project, user_1: CustomUser, user_2: CustomUser
) -> None:
    command_member.member_add_to_project(
        project=project_1, editor=user_1, email=user_2.email, role=ProjectRole.DEVELOPER
    )
    member = query_member.member_get(project_id=project_1.id, member_id=user_1.id, user=user_2)

    with pytest.raises(NotSufficientRoleInProject):
        command_member.member_remove_from_project(project=project_1, editor=user_2, member=member)


@pytest.mark.django_db
def test_member_remove_from_project_self_membership_should_fail(project_1: Project, user_1: CustomUser) -> None:
    member = query_member.member_get(project_id=project_1.id, member_id=user_1.id, user=user_1)

    with pytest.raises(UserCannotModifyOwnMembership):
        command_member.member_remove_from_project(project=project_1, editor=user_1, member=member)
