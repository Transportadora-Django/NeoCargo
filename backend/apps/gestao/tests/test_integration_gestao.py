from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from apps.contas.models import Profile, Role
from ..models import ConfiguracaoSistema, SolicitacaoMudancaPerfil, StatusSolicitacao


class FluxoCompletoSolicitacaoTest(TestCase):
    """Testes de integração para o fluxo completo de solicitações"""

    def setUp(self):
        self.client = Client()

        # Cria dono
        self.dono_user = User.objects.create_user(
            username="dono_integracao", email="dono@neocargo.com", password="testpass123"
        )
        Profile.objects.filter(user=self.dono_user).delete()
        Profile.objects.create(user=self.dono_user, role=Role.OWNER)

        # Cria cliente
        self.cliente_user = User.objects.create_user(
            username="cliente_integracao", email="cliente@test.com", password="testpass123"
        )
        Profile.objects.filter(user=self.cliente_user).delete()
        Profile.objects.create(user=self.cliente_user, role=Role.CLIENTE)

        # Garante que solicitações estão abertas
        ConfiguracaoSistema.objects.all().delete()
        config = ConfiguracaoSistema.get_config()
        config.solicitacoes_abertas = True
        config.save()

    def test_complete_approval_flow(self):
        """Testa fluxo completo de aprovação de solicitação"""
        # 1. Cria solicitação diretamente
        solicitacao = SolicitacaoMudancaPerfil.objects.create(
            usuario=self.cliente_user,
            role_atual=Role.CLIENTE,
            role_solicitada=Role.MOTORISTA,
            justificativa="Quero ser motorista da empresa",
        )

        # 2. Dono faz login e acessa dashboard
        self.client.login(username="dono_integracao", password="testpass123")
        response = self.client.get(reverse("gestao:dashboard_dono"))
        self.assertEqual(response.status_code, 200)

        # 3. Dono aprova solicitação
        approval_data = {"status": StatusSolicitacao.APROVADA, "observacoes_admin": "Documentação aprovada"}
        response = self.client.post(reverse("gestao:aprovar_solicitacao", args=[solicitacao.id]), data=approval_data)
        self.assertEqual(response.status_code, 302)

        # 4. Verifica que solicitação foi aprovada
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, StatusSolicitacao.APROVADA)
        self.assertEqual(solicitacao.aprovado_por, self.dono_user)
        self.assertEqual(solicitacao.observacoes_admin, "Documentação aprovada")

    def test_complete_rejection_flow(self):
        """Testa fluxo completo de rejeição de solicitação"""
        # 1. Cria solicitação diretamente
        solicitacao = SolicitacaoMudancaPerfil.objects.create(
            usuario=self.cliente_user,
            role_atual=Role.CLIENTE,
            role_solicitada=Role.MOTORISTA,
            justificativa="Documentação incompleta",
        )

        # 2. Dono rejeita solicitação
        self.client.login(username="dono_integracao", password="testpass123")
        rejection_data = {"status": StatusSolicitacao.REJEITADA, "observacoes_admin": "Documentação insuficiente"}
        response = self.client.post(reverse("gestao:aprovar_solicitacao", args=[solicitacao.id]), data=rejection_data)
        self.assertEqual(response.status_code, 302)

        # 3. Verifica rejeição
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, StatusSolicitacao.REJEITADA)
        self.assertEqual(solicitacao.observacoes_admin, "Documentação insuficiente")

    def test_flow_when_requests_closed(self):
        """Testa fluxo quando solicitações estão fechadas"""
        # 1. Dono fecha solicitações
        self.client.login(username="dono_integracao", password="testpass123")
        response = self.client.post(reverse("gestao:toggle_solicitacoes"))
        self.assertEqual(response.status_code, 302)

        # 2. Verifica que foi fechado
        config = ConfiguracaoSistema.get_config()
        self.assertFalse(config.solicitacoes_abertas)

        # 3. Cliente tenta acessar formulário
        self.client.login(username="cliente_integracao", password="testpass123")
        response = self.client.get(reverse("gestao:solicitar_mudanca"))
        self.assertEqual(response.status_code, 302)  # Redirect

        # 4. Dono reabre solicitações
        self.client.login(username="dono_integracao", password="testpass123")
        response = self.client.post(reverse("gestao:toggle_solicitacoes"))
        self.assertEqual(response.status_code, 302)

        # 5. Verifica que foi reaberto
        config.refresh_from_db()
        self.assertTrue(config.solicitacoes_abertas)

    def test_duplicate_request_prevention(self):
        """Testa prevenção de solicitações duplicadas"""
        # 1. Cria primeira solicitação diretamente
        SolicitacaoMudancaPerfil.objects.create(
            usuario=self.cliente_user,
            role_atual=Role.CLIENTE,
            role_solicitada=Role.MOTORISTA,
            justificativa="Primeira solicitação",
        )

        # 2. Cliente tenta acessar formulário
        self.client.login(username="cliente_integracao", password="testpass123")
        response = self.client.get(reverse("gestao:solicitar_mudanca"))
        self.assertEqual(response.status_code, 302)  # Redirect para minhas solicitações

        # 3. Verifica que só existe uma solicitação
        count = SolicitacaoMudancaPerfil.objects.filter(usuario=self.cliente_user).count()
        self.assertEqual(count, 1)


class FluxoGestaoUsuariosTest(TestCase):
    """Testes de integração para gestão de usuários"""

    def setUp(self):
        self.client = Client()

        # Cria dono
        self.dono_user = User.objects.create_user(
            username="dono_gestao", email="dono_gestao@neocargo.com", password="testpass123"
        )
        Profile.objects.filter(user=self.dono_user).delete()
        Profile.objects.create(user=self.dono_user, role=Role.OWNER)

    def test_dashboard_statistics_flow(self):
        """Testa fluxo de estatísticas no dashboard"""
        # 1. Cria usuários de diferentes tipos
        cliente1 = User.objects.create_user(username="cliente1", email="cliente1@test.com", password="123")
        cliente2 = User.objects.create_user(username="cliente2", email="cliente2@test.com", password="123")
        motorista1 = User.objects.create_user(username="motorista1", email="motorista1@test.com", password="123")

        Profile.objects.filter(user__in=[cliente1, cliente2, motorista1]).delete()
        Profile.objects.create(user=cliente1, role=Role.CLIENTE)
        Profile.objects.create(user=cliente2, role=Role.CLIENTE)
        Profile.objects.create(user=motorista1, role=Role.MOTORISTA)

        # 2. Dono acessa dashboard
        self.client.login(username="dono_gestao", password="testpass123")
        response = self.client.get(reverse("gestao:dashboard_dono"))

        # 3. Verifica estatísticas
        self.assertEqual(response.context["total_clientes"], 2)
        self.assertEqual(response.context["total_motoristas"], 1)
        self.assertGreaterEqual(response.context["total_usuarios"], 4)  # 2 clientes + 1 motorista + 1 dono

    def test_user_management_flow(self):
        """Testa fluxo de gerenciamento de usuários"""
        # 1. Cria cliente com solicitação
        cliente = User.objects.create_user(username="cliente_gestao", email="cliente_gestao@test.com", password="123")
        Profile.objects.filter(user=cliente).delete()
        Profile.objects.create(user=cliente, role=Role.CLIENTE)

        solicitacao = SolicitacaoMudancaPerfil.objects.create(
            usuario=cliente, role_atual=Role.CLIENTE, role_solicitada=Role.MOTORISTA, justificativa="Teste de gestão"
        )

        # 2. Dono visualiza dashboard
        self.client.login(username="dono_gestao", password="testpass123")
        response = self.client.get(reverse("gestao:dashboard_dono"))
        self.assertEqual(response.status_code, 200)

        # 3. Dono aprova solicitação
        approval_data = {"status": StatusSolicitacao.APROVADA, "observacoes_admin": "Aprovado para motorista"}
        response = self.client.post(reverse("gestao:aprovar_solicitacao", args=[solicitacao.id]), data=approval_data)

        # 4. Verifica aprovação
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, StatusSolicitacao.APROVADA)
        self.assertEqual(solicitacao.aprovado_por, self.dono_user)
