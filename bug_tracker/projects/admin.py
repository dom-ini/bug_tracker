from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext as _
from projects.models import Project, ProjectIdentifier, ProjectRoleAssignment


class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "project_url", "created_by", "created_at"]
    list_filter = ["status"]
    search_fields = ["name"]

    @admin.display(description=_("Url"))
    def project_url(self, obj: Project) -> str:
        return format_html("<a href='{0}' target='_blank'>{0}</a>", obj.url)


class ProjectIdentifierAdmin(admin.ModelAdmin):
    list_display = ["subdomain", "project"]
    search_fields = ["subdomain"]


class ProjectRoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "project"]
    list_filter = ["role"]


admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectIdentifier, ProjectIdentifierAdmin)
admin.site.register(ProjectRoleAssignment, ProjectRoleAssignmentAdmin)
