from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Cria automaticamente um Profile quando um User é criado.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Salva o Profile quando o User é salvo.
    """
    if hasattr(instance, "profile"):
        instance.profile.save()


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """
    Envia email de boas-vindas quando um usuário é criado.
    """
    if created:
        subject = "Bem-vindo ao NeoCargo!"
        message = f"""
        Olá {instance.get_full_name() or instance.username},

        Seja bem-vindo ao NeoCargo! Sua conta foi criada com sucesso.

        Agora você pode fazer login e começar a usar nossa plataforma.

        Atenciosamente,
        Equipe NeoCargo
        """

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't break the user creation process
            print(f"Erro ao enviar email de boas-vindas: {e}")
