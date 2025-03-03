from projects.models import Project


def project_get(pk: int) -> Project:
    return Project.objects.get(pk=pk)
