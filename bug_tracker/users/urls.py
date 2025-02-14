from django.urls import include, path
from django.views.generic import TemplateView
from users.views import CustomRegisterView

urlpatterns = [
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", CustomRegisterView.as_view(), name="rest_register"),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path(
        "auth/password-reset/confirm/<uidb64>/<token>/",
        TemplateView.as_view(template_name="password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
]
