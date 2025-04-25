from django.urls import include, path
from django.views.generic import TemplateView
from users.views import CustomPasswordResetView, CustomRegisterView, CustomResendEmailVerificationView

urlpatterns = [
    path("password/reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("", include("dj_rest_auth.urls")),
    path("registration/", CustomRegisterView.as_view(), name="register"),
    path("registration/resend-email/", CustomResendEmailVerificationView.as_view(), name="resend_email"),
    path("registration/", include("dj_rest_auth.registration.urls")),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        TemplateView.as_view(template_name="password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
]
