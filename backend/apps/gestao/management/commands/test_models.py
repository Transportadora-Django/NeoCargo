from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.contas.models import Profile, Role
from apps.gestao.models import ConfiguracaoSistema, SolicitacaoMudancaPerfil, StatusSolicitacao


class Command(BaseCommand):
    help = "Testa se os modelos estão funcionando corretamente"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Iniciando testes dos modelos..."))

        try:
            # Teste ConfiguracaoSistema
            self.stdout.write("\n🧪 Testando ConfiguracaoSistema...")
            config = ConfiguracaoSistema.get_config()
            self.stdout.write(f"✅ Config criada: {config}")
            self.stdout.write(f"✅ Solicitações abertas: {config.solicitacoes_abertas}")

            # Teste alteração
            original_status = config.solicitacoes_abertas
            config.solicitacoes_abertas = not original_status
            config.save()
            self.stdout.write(f"✅ Config alterada para: {config.solicitacoes_abertas}")

            # Restaura status original
            config.solicitacoes_abertas = original_status
            config.save()

            # Teste SolicitacaoMudancaPerfil
            self.stdout.write("\n🧪 Testando SolicitacaoMudancaPerfil...")

            # Busca ou cria usuário de teste
            user, created = User.objects.get_or_create(
                username="teste_models",
                defaults={"email": "teste@models.com", "first_name": "Teste", "last_name": "Models"},
            )
            if created:
                user.set_password("123456")
                user.save()
                self.stdout.write(f"✅ Usuário criado: {user}")
            else:
                self.stdout.write(f"✅ Usuário encontrado: {user}")

            # Busca ou cria perfil
            profile, created = Profile.objects.get_or_create(user=user, defaults={"role": Role.CLIENTE})
            if created:
                self.stdout.write(f"✅ Perfil criado: {profile}")
            else:
                self.stdout.write(f"✅ Perfil encontrado: {profile}")

            # Limpa solicitações antigas do usuário de teste
            SolicitacaoMudancaPerfil.objects.filter(usuario=user).delete()

            # Cria nova solicitação
            solicitacao = SolicitacaoMudancaPerfil.objects.create(
                usuario=user,
                role_atual=Role.CLIENTE,
                role_solicitada=Role.MOTORISTA,
                justificativa="Teste de solicitação via comando",
                telefone="(11) 99999-9999",
                cpf="123.456.789-10",
            )
            self.stdout.write(f"✅ Solicitação criada: {solicitacao}")
            self.stdout.write(f"✅ Status: {solicitacao.status}")
            self.stdout.write(f"✅ ID: {solicitacao.id}")

            # Teste de aprovação
            solicitacao.status = StatusSolicitacao.APROVADA
            solicitacao.aprovado_por = user
            solicitacao.observacoes_admin = "Teste de aprovação"
            solicitacao.save()
            self.stdout.write(f"✅ Solicitação aprovada: {solicitacao.status}")

            # Limpa dados de teste
            solicitacao.delete()
            self.stdout.write("✅ Dados de teste limpos")

            self.stdout.write(self.style.SUCCESS("\n🎉 Todos os testes passaram com sucesso!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Erro nos testes: {e}"))
            import traceback

            self.stdout.write(self.style.ERROR(traceback.format_exc()))
            raise e
