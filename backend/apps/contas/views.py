from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .forms import SignupForm
from .models import Role


@require_http_methods(["GET", "POST"])
@csrf_protect
@never_cache
def signup(request):
    """
    View para cadastro de novos usuários.
    Todos os usuários são cadastrados automaticamente como cliente.
    """
    if request.user.is_authenticated:
        # Se já estiver logado, redireciona para o dashboard
        return redirect("dashboard_cliente")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            # Check honeypot
            if form.cleaned_data.get("website"):
                messages.error(request, "Erro de segurança detectado.")
                return render(request, "contas/signup.html", {"form": form})

            user = form.save()

            # Autentica o usuário automaticamente
            login(request, user)

            messages.success(request, f"Bem-vindo, {user.get_full_name()}! Sua conta foi criada com sucesso.")

            # Todos os novos usuários são clientes, então sempre redireciona para dashboard_cliente
            return redirect("dashboard_cliente")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = SignupForm()

    return render(request, "contas/signup.html", {"form": form})


@method_decorator(never_cache, name="dispatch")
class CustomLoginView(LoginView):
    """
    View customizada para login.
    """

    template_name = "contas/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        """
        Redireciona baseado no role do usuário.
        """
        user = self.request.user
        if hasattr(user, "profile"):
            profile = user.profile
            if profile.role == Role.CLIENTE:
                return reverse("dashboard_cliente")
            elif profile.role == Role.MOTORISTA:
                return reverse("dashboard_motorista")
            elif profile.role == Role.GERENTE:
                return reverse("dashboard_gerente")
            elif profile.role == Role.OWNER:
                return reverse("dashboard_owner")

        # Fallback para dashboard_cliente
        return reverse("dashboard_cliente")

    def form_valid(self, form):
        """
        Security check and login.
        """
        response = super().form_valid(form)
        messages.success(
            self.request, f"Bem-vindo de volta, {self.request.user.get_full_name() or self.request.user.username}!"
        )
        return response


class CustomLogoutView(LogoutView):
    """
    View customizada para logout.
    """

    next_page = "home"
    http_method_names = ["get", "post"]  # Permite GET e POST

    def get(self, request, *args, **kwargs):
        """
        Permite logout via GET também.
        """
        if request.user.is_authenticated:
            messages.info(request, "Você foi desconectado com sucesso.")
        return super().post(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    """
    View customizada para solicitação de reset de senha.
    """

    template_name = "contas/password_reset.html"
    email_template_name = "contas/email/password_reset_email.html"
    subject_template_name = "contas/email/password_reset_subject.txt"
    success_url = reverse_lazy("contas:password_reset_done")

    def form_valid(self, form):
        messages.success(
            self.request, "Se este e-mail estiver cadastrado, você receberá instruções para redefinir sua senha."
        )
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    View customizada para confirmação de envio do email de reset.
    """

    template_name = "contas/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    View customizada para confirmar nova senha.
    """

    template_name = "contas/password_reset_confirm.html"
    success_url = reverse_lazy("contas:password_reset_complete")

    def form_valid(self, form):
        messages.success(self.request, "Sua senha foi alterada com sucesso! Você já pode fazer login.")
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    View customizada para completar o reset de senha.
    """

    template_name = "contas/password_reset_complete.html"
