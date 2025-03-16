from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress, EmailConfirmationHMAC, get_emailconfirmation_model
from core.utils import generate_username
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import transaction
from projects.models import Project, ProjectRole, ProjectRoleAssignment
from projects.selectors.project import project_is_manager
from projects.services.emails import send_invitation_email_for_existing_user, send_invitation_email_for_new_user
from projects.services.exceptions import (
    MemberAlreadyInProject,
    NotSufficientRoleInProject,
    UserCannotModifyOwnMembership,
)


def _get_user_by_email(email: str) -> AbstractBaseUser | None:
    email_obj = EmailAddress.objects.filter(email=email, primary=True).first()
    return email_obj.user if email_obj else None


def _generate_unique_username() -> str:
    while True:
        username = generate_username()
        if not get_user_model().objects.filter(username=username).exists():
            return username


def _create_user_without_password(email: str) -> AbstractBaseUser:
    username = _generate_unique_username()
    user = get_user_model().objects.create_user(username=username, email=email, is_active=True)
    EmailAddress.objects.create(user=user, email=email, verified=False, primary=True)
    return user


def _create_email_confirmation(*, user: AbstractBaseUser, email: str) -> EmailConfirmationHMAC:
    model = get_emailconfirmation_model()
    email_address = EmailAddress.objects.get(user=user, email=email)
    email_confirmation = model.create(email_address=email_address)
    return email_confirmation


def _is_user_in_project(*, user: AbstractBaseUser | None, project: Project) -> bool:
    if user is None:
        return False
    return ProjectRoleAssignment.objects.filter(user=user, project=project).exists()


def _create_role_assignment(*, user: AbstractBaseUser, project: Project, role: ProjectRole) -> ProjectRoleAssignment:
    role_assignment = ProjectRoleAssignment(project=project, user=user, role=role)
    role_assignment.validate_and_save()
    return role_assignment


def _update_role_assignment(*, member: ProjectRoleAssignment, new_role: ProjectRole) -> ProjectRoleAssignment:
    member.role = new_role
    member.validate_and_save()
    return member


@transaction.atomic
def member_add_to_project(
    *, project: Project, editor: AbstractBaseUser, email: str, role: ProjectRole
) -> ProjectRoleAssignment:
    if not project_is_manager(project=project, user=editor):
        raise NotSufficientRoleInProject()

    user = _get_user_by_email(email)
    if _is_user_in_project(user=user, project=project):
        raise MemberAlreadyInProject()

    if user is None:
        user = _create_user_without_password(email)
        password_token = default_token_generator.make_token(user)
        email_confirmation = _create_email_confirmation(user=user, email=email)
        send_invitation_email_for_new_user(
            email=email,
            username=user.get_username(),
            user_id=user.pk,
            password_token=password_token,
            email_confirm_token=email_confirmation.key,
            project_name=project.name,
        )
    else:
        send_invitation_email_for_existing_user(email=email, project_name=project.name)

    role_assignment = _create_role_assignment(user=user, project=project, role=role)
    return role_assignment


@transaction.atomic
def member_change_role_in_project(
    *, project: Project, editor: AbstractBaseUser, member: ProjectRoleAssignment, new_role: ProjectRole
) -> ProjectRoleAssignment:
    if not project_is_manager(project=project, user=editor):
        raise NotSufficientRoleInProject()

    if member.user == editor:
        raise UserCannotModifyOwnMembership()

    _update_role_assignment(member=member, new_role=new_role)
    return member


@transaction.atomic
def member_remove_from_project(*, project: Project, editor: AbstractBaseUser, member: ProjectRoleAssignment) -> None:
    if not project_is_manager(project=project, user=editor):
        raise NotSufficientRoleInProject()

    if member.user == editor:
        raise UserCannotModifyOwnMembership()

    member.delete()
