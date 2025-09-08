from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

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
    Envia email de boas-vindas HTML bonito quando um usuário é criado.
    """
    if created and instance.email:
        subject = "🎉 Bem-vindo ao NeoCargo!"

        # Context para o template
        context = {
            "user": instance,
            "protocol": "https" if getattr(settings, "SECURE_SSL_REDIRECT", False) else "http",
            "domain": (
                getattr(settings, "ALLOWED_HOSTS", ["localhost:8000"])[0]
                if getattr(settings, "ALLOWED_HOSTS")
                else "localhost:8000"
            ),
        }

        try:
            # Renderizar template HTML
            html_content = render_to_string("contas/email/welcome_email.html", context)

            # Criar versão texto simples como fallback
            text_content = f"""
Olá {instance.get_full_name() or instance.username},

🎉 Bem-vindo ao NeoCargo!

Sua conta foi criada com sucesso e já está pronta para uso.
Com o NeoCargo, você pode gerenciar seus fretes, acompanhar entregas e muito mais, tudo em um só lugar.

Recursos disponíveis:
• 📦 Gestão de Fretes - Organize e acompanhe todos os seus fretes
• 🚚 Rastreamento - Monitore entregas em tempo real
• 📊 Relatórios - Acesse dados detalhados para decisões estratégicas
• ⚡ Automação - Automatize processos e economize tempo

Acesse sua conta: {context["protocol"]}://{context["domain"]}/dashboard/

Próximos passos recomendados:
1. Complete seu perfil - Adicione informações da sua empresa
2. Explore a plataforma - Familiarize-se com as funcionalidades
3. Configure suas preferências - Personalize sua experiência
4. Cadastre seu primeiro frete - Comece a usar o sistema

Precisa de ajuda? Nossa equipe de suporte está pronta para ajudar!

Atenciosamente,
Equipe NeoCargo 🚛
            """.strip()

            # Criar email multipart (HTML + texto)
            email = EmailMultiAlternatives(
                subject=subject, body=text_content, from_email=settings.DEFAULT_FROM_EMAIL, to=[instance.email]
            )

            # Anexar versão HTML
            email.attach_alternative(html_content, "text/html")

            # Enviar email
            email.send(fail_silently=False)

        except Exception as e:
            # Log the error but don't break the user creation process
            print(f"Erro ao enviar email de boas-vindas: {e}")

            # Fallback para email simples em caso de erro
            try:
                message = (
                    f"Olá {instance.get_full_name() or instance.username},\n\n"
                    "Seja bem-vindo ao NeoCargo! Sua conta foi criada com sucesso.\n\n"
                    "Atenciosamente,\nEquipe NeoCargo"
                )
                send_mail(
                    subject="Bem-vindo ao NeoCargo!",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.email],
                    fail_silently=True,
                )
            except Exception:
                pass  # Se falhar completamente, não quebrar o processo
