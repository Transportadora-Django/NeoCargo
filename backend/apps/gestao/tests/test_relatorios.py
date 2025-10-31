"""
Testes para a funcionalidade de relatórios gerenciais
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

from apps.contas.models import Profile, Role
from apps.pedidos.models import Pedido, StatusPedido
from apps.gestao.relatorios import RelatorioGerencial


@pytest.mark.django_db
class TestRelatoriosView:
    """Testes para a view de relatórios"""

    @pytest.fixture
    def dono_user(self):
        """Cria um usuário dono"""
        User.objects.filter(username="dono_test").delete()
        user = User.objects.create_user(username="dono_test", password="testpass123", email="dono@test.com")
        profile, created = Profile.objects.get_or_create(user=user)
        profile.role = Role.OWNER
        profile.save()
        # Force refresh para evitar cache
        user.refresh_from_db()
        return user

    @pytest.fixture
    def gerente_user(self):
        """Cria um usuário gerente"""
        User.objects.filter(username="gerente_test").delete()
        user = User.objects.create_user(username="gerente_test", password="testpass123", email="gerente@test.com")
        profile, created = Profile.objects.get_or_create(user=user)
        profile.role = Role.GERENTE
        profile.save()
        # Force refresh para evitar cache
        user.refresh_from_db()
        return user

    @pytest.fixture
    def cliente_user(self):
        """Cria um usuário cliente"""
        User.objects.filter(username="cliente_test").delete()
        user = User.objects.create_user(username="cliente_test", password="testpass123", email="cliente@test.com")
        profile, created = Profile.objects.get_or_create(user=user)
        profile.role = Role.CLIENTE
        profile.save()
        return user

    def test_dono_pode_acessar_relatorios(self, client, dono_user):
        """Testa se o dono pode acessar a página de relatórios"""
        client.force_login(dono_user)
        url = reverse("gestao:relatorios")
        response = client.get(url)

        assert response.status_code == 200
        assert "Relatórios Gerenciais" in response.content.decode()

    def test_gerente_pode_acessar_relatorios(self, client, gerente_user):
        """Testa se o gerente pode acessar a página de relatórios"""
        client.force_login(gerente_user)
        url = reverse("gestao:relatorios")
        response = client.get(url)

        assert response.status_code == 200
        assert "Relatórios Gerenciais" in response.content.decode()

    def test_cliente_nao_pode_acessar_relatorios(self, client, cliente_user):
        """Testa se o cliente não pode acessar relatórios"""
        client.force_login(cliente_user)
        url = reverse("gestao:relatorios")
        response = client.get(url)

        assert response.status_code == 302  # Redirect
        # Pode redirecionar para home ou para /
        assert response.url in ["/", reverse("home")]

    def test_relatorios_tem_dados_financeiros(self, client, dono_user):
        """Testa se os dados financeiros aparecem no relatório"""
        client.force_login(dono_user)
        url = reverse("gestao:relatorios")
        response = client.get(url)

        assert response.status_code == 200
        assert "relatorio" in response.context
        assert "financeiro" in response.context["relatorio"]
        assert "total_receita" in response.context["relatorio"]["financeiro"]
        assert "total_pedidos" in response.context["relatorio"]["financeiro"]
        assert "ticket_medio" in response.context["relatorio"]["financeiro"]

    def test_relatorios_tem_dados_operacionais(self, client, dono_user):
        """Testa se os dados operacionais aparecem no relatório"""
        client.force_login(dono_user)
        url = reverse("gestao:relatorios")
        response = client.get(url)

        assert response.status_code == 200
        relatorio = response.context["relatorio"]
        assert "veiculos" in relatorio
        assert "motoristas" in relatorio
        assert "problemas" in relatorio

    def test_filtro_periodo_funciona(self, client, dono_user):
        """Testa se o filtro de período funciona"""
        client.force_login(dono_user)
        url = reverse("gestao:relatorios")

        # Testar diferentes períodos
        for periodo in ["7dias", "30dias", "90dias", "ano", "todos"]:
            response = client.get(url, {"periodo": periodo})
            assert response.status_code == 200
            assert response.context["periodo_selecionado"] == periodo

    def test_filtro_ano_funciona(self, client, dono_user):
        """Testa se o filtro de ano funciona"""
        client.force_login(dono_user)
        url = reverse("gestao:relatorios")
        ano_teste = 2024

        response = client.get(url, {"ano": ano_teste})
        assert response.status_code == 200
        assert response.context["ano_selecionado"] == ano_teste


@pytest.mark.django_db
class TestRelatorioGerencial:
    """Testes para a classe RelatorioGerencial"""

    @pytest.fixture
    def cliente_user(self):
        """Cria um usuário cliente"""
        User.objects.filter(username="cliente_relatorio").delete()
        user = User.objects.create_user(
            username="cliente_relatorio", password="testpass123", email="cliente@relatorio.com"
        )
        profile, created = Profile.objects.get_or_create(user=user)
        profile.role = Role.CLIENTE
        profile.save()
        return user

    @pytest.fixture
    def pedido_concluido(self, cliente_user):
        """Cria um pedido concluído para testes"""
        return Pedido.objects.create(
            cliente=cliente_user,
            cidade_origem="São Paulo",
            cidade_destino="Rio de Janeiro",
            peso_carga=Decimal("1000.00"),
            prazo_desejado=3,
            status=StatusPedido.CONCLUIDO,
            preco_final=Decimal("500.00"),
        )

    def test_get_resumo_financeiro_sem_pedidos(self):
        """Testa resumo financeiro sem pedidos"""
        resultado = RelatorioGerencial.get_resumo_financeiro()

        assert resultado["total_receita"] == Decimal("0.00")
        assert resultado["total_pedidos"] == 0
        assert resultado["ticket_medio"] == Decimal("0.00")

    def test_get_resumo_financeiro_com_pedidos(self, pedido_concluido):
        """Testa resumo financeiro com pedidos"""
        resultado = RelatorioGerencial.get_resumo_financeiro()

        assert resultado["total_receita"] == Decimal("500.00")
        assert resultado["total_pedidos"] == 1
        assert resultado["ticket_medio"] == Decimal("500.00")

    def test_get_estatisticas_pedidos(self, pedido_concluido):
        """Testa estatísticas de pedidos"""
        resultado = RelatorioGerencial.get_estatisticas_pedidos()

        assert resultado["total_geral"] >= 1
        assert resultado["total_concluidos"] >= 1
        assert "por_status" in resultado

    def test_get_estatisticas_veiculos(self):
        """Testa estatísticas de veículos"""
        resultado = RelatorioGerencial.get_estatisticas_veiculos()

        assert "total_veiculos" in resultado
        assert "veiculos_ativos" in resultado
        assert "veiculos_inativos" in resultado
        assert "taxa_utilizacao" in resultado

    def test_get_estatisticas_motoristas(self):
        """Testa estatísticas de motoristas"""
        resultado = RelatorioGerencial.get_estatisticas_motoristas()

        assert "total_motoristas" in resultado
        assert "motoristas_ativos" in resultado
        assert "motoristas_inativos" in resultado

    def test_get_estatisticas_problemas(self):
        """Testa estatísticas de problemas"""
        resultado = RelatorioGerencial.get_estatisticas_problemas()

        assert "total_problemas" in resultado
        assert "pendentes" in resultado
        assert "em_analise" in resultado
        assert "resolvidos" in resultado
        assert "taxa_resolucao" in resultado

    def test_get_pedidos_por_mes(self):
        """Testa obtenção de pedidos por mês"""
        ano = timezone.now().year
        resultado = RelatorioGerencial.get_pedidos_por_mes(ano)

        assert isinstance(resultado, list)
        assert len(resultado) == 12  # 12 meses

    def test_get_receita_por_mes(self):
        """Testa obtenção de receita por mês"""
        ano = timezone.now().year
        resultado = RelatorioGerencial.get_receita_por_mes(ano)

        assert isinstance(resultado, list)
        assert len(resultado) == 12  # 12 meses

    def test_get_relatorio_completo(self, pedido_concluido):
        """Testa obtenção do relatório completo"""
        resultado = RelatorioGerencial.get_relatorio_completo()

        assert "financeiro" in resultado
        assert "pedidos" in resultado
        assert "veiculos" in resultado
        assert "motoristas" in resultado
        assert "problemas" in resultado
        assert "pedidos_por_mes" in resultado
        assert "receita_por_mes" in resultado
        assert "tem_dados_ano" in resultado
        assert "tem_dados_financeiros" in resultado

        # Verificar que tem_dados_financeiros está correto
        assert resultado["tem_dados_financeiros"] is True  # pedido_concluido existe

    def test_get_periodo_datas_7dias(self):
        """Testa cálculo de período para 7 dias"""
        data_inicio, data_fim = RelatorioGerencial.get_periodo_datas("7dias")

        assert data_inicio is not None
        assert data_fim is not None
        diferenca = data_fim - data_inicio
        assert diferenca.days == 7

    def test_get_periodo_datas_todos(self):
        """Testa período 'todos' (sem data de início)"""
        data_inicio, data_fim = RelatorioGerencial.get_periodo_datas("todos")

        assert data_inicio is None
        assert data_fim is not None
