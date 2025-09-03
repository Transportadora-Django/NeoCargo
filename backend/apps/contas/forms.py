from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings


class SignupForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        label="Nome completo",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Digite seu nome completo"}),
    )

    email = forms.EmailField(
        required=True,
        label="E-mail",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Digite seu e-mail"}),
    )

    # Honeypot field for basic security
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ("full_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize password fields
        self.fields["password1"].widget.attrs.update({"class": "form-control", "placeholder": "Digite sua senha"})
        self.fields["password2"].widget.attrs.update({"class": "form-control", "placeholder": "Confirme sua senha"})

        # Update labels
        self.fields["password1"].label = "Senha"
        self.fields["password2"].label = "Confirmar senha"

        # Remove username field from parent class
        if "username" in self.fields:
            del self.fields["username"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower().strip()
            if User.objects.filter(email=email).exists():
                raise ValidationError("Este e-mail já está em uso.")
        return email

    def clean_website(self):
        # Honeypot field - should be empty
        website = self.cleaned_data.get("website")
        if website:
            raise ValidationError("Spam detectado.")
        return website

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name")
        if full_name:
            full_name = full_name.strip()
            if len(full_name.split()) < 2:
                raise ValidationError("Por favor, digite seu nome completo.")
        return full_name

    def save(self, commit=True):
        user = super().save(commit=False)

        # Use email as username
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]

        # Set full name
        full_name = self.cleaned_data["full_name"]
        name_parts = full_name.split()
        user.first_name = name_parts[0]
        if len(name_parts) > 1:
            user.last_name = " ".join(name_parts[1:])

        if commit:
            user.save()

        return user


class CustomPasswordResetForm(PasswordResetForm):
    """
    Formulário customizado para reset de senha que envia emails HTML.
    """

    def save(
        self,
        domain_override=None,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="registration/password_reset_email.html",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Override do método save para enviar emails HTML usando EmailMultiAlternatives
        """
        email = self.cleaned_data["email"]

        # Busca usuários ativos com este email
        active_users = self.get_users(email)

        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override

        for user in active_users:
            # Contexto para os templates
            context = {
                "email": email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }

            # Renderiza o assunto do email
            subject = render_to_string(subject_template_name, context)
            subject = "".join(subject.splitlines())  # Remove quebras de linha

            # Renderiza o template HTML
            html_content = render_to_string("contas/email/password_reset_email.html", context)

            # Renderiza o template de texto simples
            text_content = render_to_string("contas/email/password_reset_email.txt", context)

            # Cria o email multipart
            email_message = EmailMultiAlternatives(
                subject=subject, body=text_content, from_email=from_email or settings.DEFAULT_FROM_EMAIL, to=[email]
            )

            # Anexa a versão HTML
            email_message.attach_alternative(html_content, "text/html")

            # Envia o email
            email_message.send(fail_silently=False)
