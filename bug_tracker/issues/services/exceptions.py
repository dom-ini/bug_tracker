from core.exceptions import ApplicationException
from django.utils.translation import gettext_lazy as _


class AssigneeDoesNotExistWithinProject(ApplicationException):
    message = _("Given assignee does not belong to the project.")


class IssueAlreadyAssignedToGivenAssignee(ApplicationException):
    message = _("Given assignee is already assigned to this issue.")


class ModelActionNotPermitted(ApplicationException):
    MODEL_NAME = _("object")
    message = _("User does not have required permissions to perform this action on {model_name}: {action}")

    def __init__(self, action: str) -> None:
        message = self.message.format(action=action, model_name=self.MODEL_NAME)
        super().__init__(message)


class IssueActionNotPermitted(ModelActionNotPermitted):
    MODEL_NAME = _("issue")

    EDIT = _("edit")
    CREATE = _("create")
    ASSIGN = _("assign")
    REMOVE = _("remove")


class CommentActionNotPermitted(ModelActionNotPermitted):
    MODEL_NAME = _("comment")

    EDIT = _("edit")
    REMOVE = _("remove")
