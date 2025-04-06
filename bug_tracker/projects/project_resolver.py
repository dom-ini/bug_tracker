from django.conf import settings
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from projects.models import Project
from projects.services.query_project import project_get_by_subdomain


class MissingProjectIdentifierHeader(Exception):
    pass


def resolve_project_from_header(request: HttpRequest) -> Project | None:
    header_name = settings.SUBDOMAIN_HEADER_NAME
    subdomain = request.headers.get(header_name)
    if not subdomain:
        raise MissingProjectIdentifierHeader(_("Missing %(header_name)s header") % {"header_name": header_name})

    return project_get_by_subdomain(subdomain=subdomain, user=request.user)
