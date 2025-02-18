from django.urls import include, path
from django.views.generic import TemplateView
from users.views import CustomPasswordResetView, CustomRegisterView, CustomResendEmailVerificationView

urlpatterns = [
    path("auth/password/reset/", CustomPasswordResetView.as_view(), name="rest_password_reset"),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", CustomRegisterView.as_view(), name="rest_register"),
    path("auth/registration/resend-email/", CustomResendEmailVerificationView.as_view(), name="rest_resend_email"),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path(
        "auth/password-reset/confirm/<uidb64>/<token>/",
        TemplateView.as_view(template_name="password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
]
