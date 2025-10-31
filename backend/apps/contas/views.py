from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
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
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.utils import timezone

from .forms import SignupForm, CustomPasswordResetForm, UserEditForm, ProfileEditForm, CustomPasswordChangeForm
from .models import Role, Profile, EmailChangeRequest


def send_email_change_confirmation(email_change_request, request):
    """
    Envia email de confirmação de mudança para o email antigo.
    """
    import logging

    logger = logging.getLogger(__name__)

    # Debug: configurações de email
    logger.info(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Not set')}")
    logger.info(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    logger.info(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")

    current_site = get_current_site(request)

    # URL de confirmação
    confirmation_url = request.build_absolute_uri(
        reverse("contas:confirmar_mudanca_email", kwargs={"token": email_change_request.token})
    )

    context = {
        "user_name": email_change_request.user.get_full_name() or email_change_request.user.username,
        "old_email": email_change_request.old_email,
        "new_email": email_change_request.new_email,
        "confirmation_url": confirmation_url,
        "site_name": current_site.name,
        "domain": current_site.domain,
        "protocol": "https" if request.is_secure() else "http",
        "expires_at": email_change_request.expires_at,
    }

    # Renderiza o assunto
    subject = f"Confirme a alteração de email - {current_site.name}"

    # Renderiza os templates
    try:
        html_content = render_to_string("contas/email/email_change_confirmation.html", context)
        text_content = render_to_string("contas/email/email_change_confirmation.txt", context)
        logger.info("Templates renderizados com sucesso")
    except Exception as e:
        logger.warning(f"Erro ao renderizar templates: {e}. Usando fallback.")
        # Fallback para template simples
        html_content = f"""
        <h2>Confirmação de Alteração de Email - {current_site.name}</h2>
        <p>Olá {context['user_name']},</p>
        <p>Você solicitou a alteração do email da sua conta de <strong>{email_change_request.old_email}</strong> \
para <strong>{email_change_request.new_email}</strong>.</p>
        <p><strong>Para confirmar esta alteração, clique no link abaixo:</strong></p>
        <p><a href="{confirmation_url}" \
style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">\
Confirmar Alteração</a></p>
        <p>Este link expira em \
{email_change_request.expires_at.strftime('%d/%m/%Y às %H:%M')}.</p>
        <p><strong>Se você não solicitou esta alteração, ignore este email.</strong></p>
        <p>Atenciosamente,<br>Equipe {current_site.name}</p>
        """
        text_content = f"""
        Confirmação de Alteração de Email - {current_site.name}

        Olá {context['user_name']},

        Você solicitou a alteração do email da sua conta de {email_change_request.old_email} \
para {email_change_request.new_email}.

        Para confirmar esta alteração, acesse o link abaixo:
        {confirmation_url}

        Este link expira em {email_change_request.expires_at.strftime('%d/%m/%Y às %H:%M')}.

        Se você não solicitou esta alteração, ignore este email.

        Atenciosamente,
        Equipe {current_site.name}
        """

    # Cria e envia o email
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@neocargo.local"),
        to=[email_change_request.old_email],
    )

    email_message.attach_alternative(html_content, "text/html")

    logger.info(f"Tentando enviar email para: {email_change_request.old_email}")
    logger.info(f"Assunto: {subject}")

    try:
        result = email_message.send(fail_silently=False)
        logger.info(f"Email enviado com sucesso! Resultado: {result}")
        return True
    except Exception as e:
        logger.error(f"Falha ao enviar email de confirmação: {e}")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        return False


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
        return redirect("dashboard:cliente")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            # Check honeypot
            if form.cleaned_data.get("website"):
                messages.error(request, "Erro de segurança detectado.")
                return render(request, "contas/signup.html", {"form": form})

            user = form.save()

            # Autentica o usuário automaticamente usando nosso backend customizado
            login(request, user, backend="apps.contas.backends.EmailBackend")

            messages.success(request, f"Bem-vindo, {user.get_full_name()}! Sua conta foi criada com sucesso.")

            # Todos os novos usuários são clientes, então sempre redireciona para dashboard_cliente
            return redirect("dashboard:cliente")
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

        # Se for superuser, redireciona para dashboard owner ou cria perfil se necessário
        if user.is_superuser:
            # Cria ou obtém perfil de superuser como OWNER
            from .models import Profile

            profile, created = Profile.objects.get_or_create(user=user, defaults={"role": Role.OWNER})
            if created:
                messages.info(self.request, "Perfil de administrador criado automaticamente.")
            return reverse("dashboard_owner")

        # Se for staff sem ser superuser, trata como gerente
        if user.is_staff and not hasattr(user, "profile"):
            from .models import Profile

            profile, created = Profile.objects.get_or_create(user=user, defaults={"role": Role.GERENTE})
            if created:
                messages.info(self.request, "Perfil de gerente criado automaticamente.")
            return reverse("gestao:dashboard_gerente")

        # Usuários normais com profile
        if hasattr(user, "profile"):
            profile = user.profile
            if profile.role == Role.CLIENTE:
                return reverse("dashboard:cliente")
            elif profile.role == Role.MOTORISTA:
                return reverse("motoristas:dashboard")
            elif profile.role == Role.GERENTE:
                return reverse("gestao:dashboard_gerente")
            elif profile.role == Role.OWNER:
                return reverse("gestao:dashboard_dono")

        # Fallback para dashboard_cliente
        return reverse("dashboard:cliente")

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
    form_class = CustomPasswordResetForm  # Usa o formulário customizado

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


@login_required
@require_http_methods(["GET", "POST"])
@csrf_protect
def perfil(request):
    """
    View para visualização e edição do perfil do usuário.
    Permite editar dados pessoais (nome, email) e trocar senha.
    """
    # Garante que o usuário tem um perfil
    profile, created = Profile.objects.get_or_create(user=request.user, defaults={"role": Role.CLIENTE})

    if created:
        messages.info(request, "Perfil criado automaticamente.")

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "user_data":
            # CAPTURA O EMAIL ANTIGO ANTES DE PROCESSAR O FORMULÁRIO
            old_email = request.user.email

            # Formulário de dados pessoais
            user_form = UserEditForm(request.POST, instance=request.user)
            profile_form = ProfileEditForm(instance=profile)
            password_form = CustomPasswordChangeForm(request.user)

            import logging

            logger = logging.getLogger(__name__)
            logger.info(f"DEBUG FORM - POST data: {dict(request.POST)}")
            logger.info(f"DEBUG FORM - Form is_valid: {user_form.is_valid()}")
            if not user_form.is_valid():
                logger.info(f"DEBUG FORM - Form errors: {user_form.errors}")

            if user_form.is_valid():
                # Verifica se o email foi alterado usando o email capturado ANTES do processamento
                new_email = user_form.cleaned_data["email"]

                # Comparação case-insensitive e sem espaços para evitar problemas de normalização
                old_email_normalized = old_email.lower().strip() if old_email else ""
                new_email_normalized = new_email.lower().strip() if new_email else ""
                email_changed = old_email_normalized != new_email_normalized

                logger.info(f"DEBUG - Email antigo: '{old_email}' (norm: '{old_email_normalized}')")
                logger.info(f"DEBUG - Email novo: '{new_email}' (norm: '{new_email_normalized}')")
                logger.info(f"DEBUG - Email mudou: {email_changed}")

                if email_changed:
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.info(f"Email alterado de {old_email} para {new_email}")

                    # Salva apenas os campos que não são email (nome)
                    # Processa o full_name do formulário
                    full_name = user_form.cleaned_data.get("full_name", "")
                    if full_name:
                        name_parts = full_name.split()
                        request.user.first_name = name_parts[0]
                        if len(name_parts) > 1:
                            request.user.last_name = " ".join(name_parts[1:])
                        else:
                            request.user.last_name = ""

                    # NÃO altera email nem username - mantém os valores originais
                    request.user.save(update_fields=["first_name", "last_name"])

                    # Remove solicitações anteriores não confirmadas para este usuário
                    EmailChangeRequest.objects.filter(user=request.user, confirmed=False).delete()

                    # Cria nova solicitação de mudança
                    email_change_request = EmailChangeRequest.objects.create(
                        user=request.user, old_email=old_email, new_email=new_email
                    )

                    # Envia email de confirmação
                    confirmation_sent = send_email_change_confirmation(
                        email_change_request=email_change_request, request=request
                    )

                    if confirmation_sent:
                        messages.success(
                            request,
                            f"Solicitação de alteração de email criada! "
                            f"Verifique o email {old_email} e clique no link de confirmação "
                            f"para completar a alteração.",
                        )
                    else:
                        messages.warning(
                            request, "Não foi possível enviar o email de confirmação. Tente novamente mais tarde."
                        )
                else:
                    # Se o email não mudou, salva normalmente
                    user_form.save()
                    messages.success(request, "Seus dados pessoais foram atualizados com sucesso!")

                return redirect("contas:perfil")
            else:
                messages.error(request, "Por favor, corrija os erros nos dados pessoais.")

        elif form_type == "password_change":
            # Formulário de alteração de senha
            # Preserva os dados do formulário de usuário em caso de erro de senha
            if "full_name" in request.POST and "email" in request.POST:
                user_form = UserEditForm(request.POST, instance=request.user)
            else:
                user_form = UserEditForm(instance=request.user)
            profile_form = ProfileEditForm(instance=profile)
            password_form = CustomPasswordChangeForm(request.user, request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Mantém o usuário logado após mudar a senha
                messages.success(request, "Sua senha foi alterada com sucesso!")
                return redirect("contas:perfil")
            else:
                messages.error(request, "Por favor, corrija os erros na alteração de senha.")

        else:
            # Se não especificou o tipo de formulário, inicializa todos vazios
            user_form = UserEditForm(instance=request.user)
            profile_form = ProfileEditForm(instance=profile)
            password_form = CustomPasswordChangeForm(request.user)
            messages.error(request, "Tipo de formulário inválido.")

    else:
        # GET request - mostra formulários vazios
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=profile)
        password_form = CustomPasswordChangeForm(request.user)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "password_form": password_form,
        "profile": profile,
    }

    return render(request, "contas/perfil.html", context)


@require_http_methods(["GET", "POST"])
@csrf_protect
def confirmar_mudanca_email(request, token):
    """
    View para confirmar a mudança de email através do token enviado por email.
    """
    try:
        email_request = EmailChangeRequest.objects.get(token=token)
    except EmailChangeRequest.DoesNotExist:
        messages.error(request, "Link de confirmação inválido ou expirado.")
        return redirect("contas:login")

    # Verifica se o token é válido
    if not email_request.is_valid:
        if email_request.confirmed:
            messages.info(request, "Esta alteração de email já foi confirmada.")
        else:
            messages.error(request, "Link de confirmação expirado.")
        return redirect("contas:login")

    if request.method == "POST":
        # Confirma a mudança - atualiza tanto email quanto username
        email_request.user.email = email_request.new_email
        email_request.user.username = email_request.new_email  # Username = email
        email_request.user.save()

        email_request.confirmed = True
        email_request.confirmed_at = timezone.now()
        email_request.save()

        messages.success(
            request, f"Email alterado com sucesso de {email_request.old_email} para {email_request.new_email}!"
        )

        # Se o usuário estiver logado e for o mesmo da solicitação, redireciona para perfil
        if request.user.is_authenticated and request.user.id == email_request.user.id:
            return redirect("contas:perfil")
        else:
            return redirect("contas:login")

    # GET request - mostra página de confirmação
    context = {
        "email_request": email_request,
        "old_email": email_request.old_email,
        "new_email": email_request.new_email,
        "user_name": email_request.user.get_full_name() or email_request.user.username,
    }

    return render(request, "contas/confirmar_mudanca_email.html", context)
