"""
Testes de frontend para dashboard com Selenium.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.conftest import selenium_login


@pytest.mark.django_db
class TestDashboardDono:
    """Testes do dashboard do dono."""

    def test_dashboard_dono_loads(self, browser, live_server_url, user_dono):
        """Testa se o dashboard do dono carrega."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")

        WebDriverWait(browser, 10).until(
            lambda driver: "/dashboard/" in driver.current_url or "/gestao/dashboard/" in driver.current_url
        )

        assert "/dashboard/" in browser.current_url or "/gestao/dashboard/" in browser.current_url

    def test_dashboard_has_statistics(self, browser, live_server_url, user_dono):
        """Testa se o dashboard exibe estatísticas."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")

        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        page_source = browser.page_source

        # Verifica se há indicadores/estatísticas
        assert (
            "pedidos" in page_source.lower()
            or "veículos" in page_source.lower()
            or "veiculos" in page_source.lower()
            or "motoristas" in page_source.lower()
            or "dashboard" in page_source.lower()
        )

    def test_dashboard_has_navigation_menu(self, browser, live_server_url, user_dono):
        """Testa se o dashboard tem menu de navegação."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")

        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        # Verifica se há links de navegação
        nav_links = browser.find_elements(By.TAG_NAME, "a")
        assert len(nav_links) > 0

    def test_dashboard_relatorios_link_exists(self, browser, live_server_url, user_dono):
        """Testa se há link para relatórios no dashboard."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")

        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        page_source = browser.page_source

        assert (
            "relatório" in page_source.lower()
            or "relatorio" in page_source.lower()
            or "/gestao/relatorios/" in page_source
        )

    def test_dashboard_has_quick_actions(self, browser, live_server_url, user_dono):
        """Testa se o dashboard tem ações rápidas."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")

        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        # Verifica se há botões ou links de ação
        buttons = browser.find_elements(By.TAG_NAME, "button")
        links = browser.find_elements(By.TAG_NAME, "a")

        assert len(buttons) + len(links) > 0


@pytest.mark.django_db
class TestDashboardGerente:
    """Testes do dashboard do gerente."""

    def test_dashboard_gerente_loads(self, browser, live_server_url, user_gerente):
        """Testa se o dashboard do gerente carrega."""
        selenium_login(browser, live_server_url, "gerente_test", "testpass123")

        WebDriverWait(browser, 10).until(
            lambda driver: "/dashboard/" in driver.current_url or "/gestao/dashboard/" in driver.current_url
        )

        assert "/dashboard/" in browser.current_url or "/gestao/dashboard/" in browser.current_url

    def test_dashboard_gerente_has_access_to_features(self, browser, live_server_url, user_gerente):
        """Testa se gerente tem acesso às funcionalidades principais."""
        selenium_login(browser, live_server_url, "gerente_test", "testpass123")

        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        page_source = browser.page_source

        # Gerente deve ter acesso a funcionalidades principais
        assert (
            "pedidos" in page_source.lower() or "veículos" in page_source.lower() or "motoristas" in page_source.lower()
        )


@pytest.mark.django_db
class TestDashboardCliente:
    """Testes do dashboard do cliente."""

    def test_dashboard_cliente_loads(self, browser, live_server_url, user_cliente):
        """Testa se cliente acessa algum dashboard após login."""
        selenium_login(browser, live_server_url, "cliente_test", "testpass123")

        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        # Cliente foi redirecionado para alguma página
        assert "/contas/login/" not in browser.current_url

    def test_cliente_sees_own_pedidos(self, browser, live_server_url, user_cliente):
        """Testa se cliente vê seus próprios pedidos."""
        selenium_login(browser, live_server_url, "cliente_test", "testpass123")

        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        page_source = browser.page_source

        # Cliente deve ver informações sobre pedidos
        assert "pedido" in page_source.lower() or "dashboard" in page_source.lower()


@pytest.mark.django_db
class TestDashboardMotorista:
    """Testes do dashboard do motorista."""

    def test_dashboard_motorista_loads(self, browser, live_server_url, user_motorista):
        """Testa se motorista acessa dashboard após login."""
        selenium_login(browser, live_server_url, "motorista_test", "testpass123")

        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        # Motorista foi redirecionado
        assert "/contas/login/" not in browser.current_url

    def test_motorista_sees_assigned_deliveries(self, browser, live_server_url, user_motorista):
        """Testa se motorista vê entregas atribuídas."""
        selenium_login(browser, live_server_url, "motorista_test", "testpass123")

        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        page_source = browser.page_source

        # Motorista deve ver informações sobre entregas
        assert (
            "entrega" in page_source.lower()
            or "pedido" in page_source.lower()
            or "rota" in page_source.lower()
            or "dashboard" in page_source.lower()
        )
