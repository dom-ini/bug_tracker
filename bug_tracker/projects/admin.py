from django.contrib import admin
from projects.models import Project, ProjectIdentifier, ProjectRoleAssignment

admin.site.register((Project, ProjectRoleAssignment, ProjectIdentifier))
