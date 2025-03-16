from core.models import BaseModel
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import validate_slug
from django.db import models
from django.utils.translation import gettext_lazy as _


class ProjectRole(models.TextChoices):
    MANAGER = "MNG", _("manager")
    DEVELOPER = "DEV", _("developer")
    REPORTER = "REP", _("reporter")


class Project(BaseModel):
    class Status(models.IntegerChoices):
        ACTIVE = 1, _("active")
        CLOSED = 2, _("closed")

    name = models.CharField(max_length=128)
    description = models.TextField(max_length=1024, blank=True, null=True)
    status = models.IntegerField(choices=Status, default=Status.ACTIVE)
    created_by = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, null=True, related_name="projects_created"
    )

    members = models.ManyToManyField(get_user_model(), through="ProjectRoleAssignment", related_name="projects_joined")

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    @property
    def subdomain(self) -> str:
        return self.identifier.subdomain

    @property
    def url(self) -> str:
        return f"https://{self.subdomain}.{settings.FRONT_DOMAIN}"

    def __str__(self) -> str:
        return self.name


class ProjectIdentifier(BaseModel):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="identifier")
    subdomain = models.CharField(max_length=50, unique=True, validators=[validate_slug], db_index=True)

    class Meta:
        verbose_name = _("Project identifier")
        verbose_name_plural = _("Project identifiers")

    def __str__(self) -> str:
        return self.subdomain


class ProjectRoleAssignment(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="role_assignments")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="project_roles")
    role = models.CharField(max_length=3, choices=ProjectRole)

    class Meta:
        unique_together = ("project", "user")
        verbose_name = _("Project role assignment")
        verbose_name_plural = _("Project role assignments")
        ordering = ["user_id"]

    def __str__(self) -> str:
        return f"{self.project} - {self.user} - {self.role}"
