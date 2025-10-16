from django.test import TestCase
from django.contrib.auth.models import User

from apps.contas.models import Profile, Role
from ..models import ConfiguracaoSistema, SolicitacaoMudancaPerfil, StatusSolicitacao


class ConfiguracaoSistemaModelTest(TestCase):
    """Testes para o modelo ConfiguracaoSistema"""

    def setUp(self):
        # Limpa configurações existentes
        ConfiguracaoSistema.objects.all().delete()

    def test_get_config_creates_default_configuration(self):
        """Testa se get_config cria configuração padrão quando não existe"""
        # Verifica que não existe configuração
        self.assertEqual(ConfiguracaoSistema.objects.count(), 0)

        # Chama get_config
        config = ConfiguracaoSistema.get_config()

        # Verifica que foi criada
        self.assertEqual(ConfiguracaoSistema.objects.count(), 1)
        self.assertTrue(config.solicitacoes_abertas)  # Padrão é True

    def test_get_config_returns_existing_configuration(self):
        """Testa se get_config retorna configuração existente"""
        # Cria usuário para teste
        user = User.objects.create_user(username="test_config_user", email="test@test.com", password="testpass123")

        # Cria configuração
        config_original = ConfiguracaoSistema.objects.create(solicitacoes_abertas=False, atualizado_por=user)

        # Chama get_config
        config_retornada = ConfiguracaoSistema.get_config()

        # Verifica que é a mesma
        self.assertEqual(config_original.pk, config_retornada.pk)
        self.assertFalse(config_retornada.solicitacoes_abertas)

    def test_str_method_when_open(self):
        """Testa método __str__ quando solicitações estão abertas"""
        config = ConfiguracaoSistema.objects.create(solicitacoes_abertas=True)
        self.assertEqual(str(config), "Solicitações: Abertas")

    def test_str_method_when_closed(self):
        """Testa método __str__ quando solicitações estão fechadas"""
        config = ConfiguracaoSistema.objects.create(solicitacoes_abertas=False)
        self.assertEqual(str(config), "Solicitações: Fechadas")


class SolicitacaoMudancaPerfilModelTest(TestCase):
    """Testes para o modelo SolicitacaoMudancaPerfil"""

    def setUp(self):
        # Cria usuário único para cada teste
        self.user = User.objects.create_user(
            username="test_solicitacao_user", email="test_solicitacao@test.com", password="testpass123"
        )
        # Remove perfil se existir e cria novo
        Profile.objects.filter(user=self.user).delete()
        self.profile = Profile.objects.create(user=self.user, role=Role.CLIENTE)

    def test_create_basic_request(self):
        """Testa criação de solicitação básica"""
        solicitacao = SolicitacaoMudancaPerfil.objects.create(
            usuario=self.user,
            role_atual=Role.CLIENTE,
            role_solicitada=Role.MOTORISTA,
            justificativa="Quero ser motorista da empresa",
            telefone="(11) 99999-9999",
            cpf="123.456.789-10",
        )

        self.assertEqual(solicitacao.usuario, self.user)
        self.assertEqual(solicitacao.role_atual, Role.CLIENTE)
        self.assertEqual(solicitacao.role_solicitada, Role.MOTORISTA)
        self.assertEqual(solicitacao.status, StatusSolicitacao.PENDENTE)
        self.assertEqual(solicitacao.telefone, "(11) 99999-9999")
        self.assertEqual(solicitacao.cpf, "123.456.789-10")

    def test_default_status_is_pending(self):
        """Testa que status padrão é PENDENTE"""
        solicitacao = SolicitacaoMudancaPerfil.objects.create(
            usuario=self.user, role_atual=Role.CLIENTE, role_solicitada=Role.MOTORISTA, justificativa="Teste"
        )
        self.assertEqual(solicitacao.status, StatusSolicitacao.PENDENTE)

    def test_optional_personal_fields(self):
        """Testa que campos pessoais são opcionais"""
        solicitacao = SolicitacaoMudancaPerfil.objects.create(
            usuario=self.user, role_atual=Role.CLIENTE, role_solicitada=Role.GERENTE, justificativa="Quero ser gerente"
        )

        self.assertIsNone(solicitacao.telefone)
        self.assertIsNone(solicitacao.cpf)
        self.assertIsNone(solicitacao.endereco)
        self.assertIsNone(solicitacao.data_nascimento)

    def test_str_method(self):
        """Testa método __str__"""
        solicitacao = SolicitacaoMudancaPerfil.objects.create(
            usuario=self.user, role_atual=Role.CLIENTE, role_solicitada=Role.MOTORISTA, justificativa="Teste"
        )

        str_result = str(solicitacao)
        self.assertIn("test_solicitacao_user", str_result)
        self.assertIn("Cliente", str_result)
        self.assertIn("Motorista", str_result)

    def test_request_approval(self):
        """Testa aprovação de solicitação"""
        # Cria dono para aprovação
        dono_user = User.objects.create_user(
            username="test_dono_approval", email="dono@test.com", password="testpass123"
        )

        solicitacao = SolicitacaoMudancaPerfil.objects.create(
            usuario=self.user, role_atual=Role.CLIENTE, role_solicitada=Role.MOTORISTA, justificativa="Teste"
        )

        # Aprova solicitação
        solicitacao.status = StatusSolicitacao.APROVADA
        solicitacao.aprovado_por = dono_user
        solicitacao.observacoes_admin = "Aprovado com sucesso"
        solicitacao.save()

        self.assertEqual(solicitacao.status, StatusSolicitacao.APROVADA)
        self.assertEqual(solicitacao.aprovado_por, dono_user)
        self.assertEqual(solicitacao.observacoes_admin, "Aprovado com sucesso")

    def test_request_rejection(self):
        """Testa rejeição de solicitação"""
        # Cria dono para rejeição
        dono_user = User.objects.create_user(
            username="test_dono_rejection", email="dono_rejection@test.com", password="testpass123"
        )

        solicitacao = SolicitacaoMudancaPerfil.objects.create(
            usuario=self.user, role_atual=Role.CLIENTE, role_solicitada=Role.MOTORISTA, justificativa="Teste"
        )

        # Rejeita solicitação
        solicitacao.status = StatusSolicitacao.REJEITADA
        solicitacao.aprovado_por = dono_user
        solicitacao.observacoes_admin = "Documentação insuficiente"
        solicitacao.save()

        self.assertEqual(solicitacao.status, StatusSolicitacao.REJEITADA)
        self.assertEqual(solicitacao.aprovado_por, dono_user)
        self.assertEqual(solicitacao.observacoes_admin, "Documentação insuficiente")
