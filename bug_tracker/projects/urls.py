from django.urls import include, path
from projects.views import ProjectViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("projects", ProjectViewSet, basename="projects")

urlpatterns = [path("", include(router.urls))]
