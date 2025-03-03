from typing import Any

from django.http import HttpRequest
from projects.models import Project, ProjectRole
from rest_framework import permissions
from rest_framework.permissions import BasePermission


class CanEditProject(BasePermission):
    def has_object_permission(self, request: HttpRequest, _view: Any, obj: Project) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.has_role(user=request.user, role=ProjectRole.MANAGER)
