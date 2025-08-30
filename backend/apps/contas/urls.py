from django.urls import path
from . import views

app_name = "contas"

urlpatterns = [
    path("cadastro/", views.signup, name="signup"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    # Password Reset URLs
    path("esqueci-senha/", views.CustomPasswordResetView.as_view(), name="password_reset"),
    path("esqueci-senha/enviado/", views.CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "redefinir-senha/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("redefinir-senha/concluido/", views.CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
