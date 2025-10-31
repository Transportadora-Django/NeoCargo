"""
Testes de frontend para navegação do sistema com Selenium.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.conftest import selenium_login


@pytest.mark.django_db
class TestNavigationDono:
    """Testes de navegação para usuário DONO."""

    def test_access_dashboard(self, browser, live_server_url, user_dono):
        """Testa acesso ao dashboard do dono."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")

        # Aguarda carregamento do dashboard
        WebDriverWait(browser, 10).until(
            lambda driver: "/dashboard/" in driver.current_url or "/gestao/dashboard/" in driver.current_url
        )

        # Verifica se está no dashboard
        assert "/dashboard/" in browser.current_url or "/gestao/dashboard/" in browser.current_url

        # Verifica se o conteúdo do dashboard está presente
        page_text = browser.page_source
        assert "dashboard" in page_text.lower() or "painel" in page_text.lower() or "início" in page_text.lower()

    def test_access_relatorios(self, browser, live_server_url, user_dono):
        """Testa acesso à página de relatórios (NC-39)."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        # Navega para relatórios
        browser.get(f"{live_server_url}/gestao/relatorios/")

        # Aguarda carregamento da página
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Verifica se está na página de relatórios
        assert "/gestao/relatorios/" in browser.current_url

        # Verifica se o conteúdo está presente
        page_text = browser.page_source
        assert (
            "relatório" in page_text.lower()
            or "relatorio" in page_text.lower()
            or "gráfico" in page_text.lower()
            or "grafico" in page_text.lower()
        )

    def test_access_pedidos(self, browser, live_server_url, user_dono):
        """Testa acesso à página de pedidos."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        # Navega para pedidos
        browser.get(f"{live_server_url}/gestao/pedidos/")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Verifica se está na página de pedidos
        assert "/gestao/pedidos/" in browser.current_url or "/pedidos/" in browser.current_url

    def test_navigation_menu_links(self, browser, live_server_url, user_dono):
        """Testa se os links do menu de navegação funcionam."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")

        # Aguarda carregamento do dashboard
        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        # Verifica se há elementos de navegação
        nav_links = browser.find_elements(By.TAG_NAME, "a")

        assert len(nav_links) > 0, "Deve haver links de navegação na página"


@pytest.mark.django_db
class TestNavigationGerente:
    """Testes de navegação para usuário GERENTE."""

    def test_access_dashboard(self, browser, live_server_url, user_gerente):
        """Testa acesso ao dashboard do gerente."""
        selenium_login(browser, live_server_url, "gerente_test", "testpass123")

        # Aguarda carregamento do dashboard
        WebDriverWait(browser, 10).until(
            lambda driver: "/dashboard/" in driver.current_url or "/gestao/dashboard/" in driver.current_url
        )

        # Verifica se está no dashboard
        assert "/dashboard/" in browser.current_url or "/gestao/dashboard/" in browser.current_url

    def test_access_relatorios(self, browser, live_server_url, user_gerente):
        """Testa acesso à página de relatórios para gerente."""
        selenium_login(browser, live_server_url, "gerente_test", "testpass123")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        # Navega para relatórios
        browser.get(f"{live_server_url}/gestao/relatorios/")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Gerente deve ter acesso a relatórios
        assert "/gestao/relatorios/" in browser.current_url


@pytest.mark.django_db
class TestNavigationAccessControl:
    """Testes de controle de acesso na navegação."""

    def test_cliente_cannot_access_relatorios(self, browser, live_server_url, user_cliente):
        """Testa que cliente não pode acessar relatórios."""
        selenium_login(browser, live_server_url, "cliente_test", "testpass123")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        # Tenta navegar para relatórios
        browser.get(f"{live_server_url}/gestao/relatorios/")

        # Aguarda processamento
        import time

        time.sleep(2)

        # Cliente deve ser bloqueado ou redirecionado
        # Não deve estar na página de relatórios
        assert (
            "/gestao/relatorios/" not in browser.current_url
            or "403" in browser.page_source
            or "não autorizado" in browser.page_source.lower()
            or "permissão" in browser.page_source.lower()
        )

    def test_motorista_cannot_access_relatorios(self, browser, live_server_url, user_motorista):
        """Testa que motorista não pode acessar relatórios."""
        selenium_login(browser, live_server_url, "motorista_test", "testpass123")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        # Tenta navegar para relatórios
        browser.get(f"{live_server_url}/gestao/relatorios/")

        # Aguarda processamento
        import time

        time.sleep(2)

        # Motorista deve ser bloqueado ou redirecionado
        assert (
            "/gestao/relatorios/" not in browser.current_url
            or "403" in browser.page_source
            or "não autorizado" in browser.page_source.lower()
            or "permissão" in browser.page_source.lower()
        )

    def test_unauthenticated_redirects_to_login(self, browser, live_server_url):
        """Testa que usuário não autenticado é redirecionado para login."""
        # Tenta acessar página protegida sem login
        browser.get(f"{live_server_url}/gestao/dashboard/")

        # Aguarda redirecionamento
        WebDriverWait(browser, 10).until(
            lambda driver: "/contas/login/" in driver.current_url or "login" in driver.current_url.lower()
        )

        # Deve ser redirecionado para login
        assert "/contas/login/" in browser.current_url or "login" in browser.current_url.lower()
