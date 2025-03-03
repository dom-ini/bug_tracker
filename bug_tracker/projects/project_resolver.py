from django.conf import settings
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from projects.models import Project


class MissingProjectIdentifierHeader(Exception):
    pass


def resolve_project_from_header(request: HttpRequest) -> Project | None:
    header_name = settings.SUBDOMAIN_HEADER_NAME
    subdomain = request.headers.get(header_name)
    if not subdomain:
        raise MissingProjectIdentifierHeader(_(f"Missing {header_name} header"))

    try:
        return Project.objects.get_by_subdomain(subdomain)
    except Project.DoesNotExist:
        return None
