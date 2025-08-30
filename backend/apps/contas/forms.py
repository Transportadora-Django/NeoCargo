from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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
