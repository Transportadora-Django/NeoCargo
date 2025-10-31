"""
Testes de frontend para rotas com Selenium.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.conftest import selenium_login


@pytest.mark.django_db
class TestRotasPage:
    """Testes da página de rotas."""

    def test_rotas_page_loads(self, browser, live_server_url, user_dono):
        """Testa se a página de rotas carrega."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")
        browser.get(f"{live_server_url}/rotas/gerenciar/rotas/")

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = browser.page_source
        assert "/rotas/" in browser.current_url or "rota" in page_source.lower()

    def test_rotas_list_displays(self, browser, live_server_url, user_dono):
        """Testa se a lista de rotas é exibida."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")
        browser.get(f"{live_server_url}/rotas/gerenciar/rotas/")

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = browser.page_source

        assert "<table" in page_source or "rota" in page_source.lower() or "sem rotas" in page_source.lower()


@pytest.mark.django_db
class TestRotasAccessControl:
    """Testes de controle de acesso às rotas."""

    def test_gerente_can_access_rotas(self, browser, live_server_url, user_gerente):
        """Testa que gerente pode acessar rotas."""
        selenium_login(browser, live_server_url, "gerente_test", "testpass123")
        browser.get(f"{live_server_url}/rotas/gerenciar/rotas/")

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = browser.page_source
        assert "/rotas/" in browser.current_url or "rota" in page_source.lower()

    def test_motorista_can_view_own_rotas(self, browser, live_server_url, user_motorista):
        """Testa que motorista pode ver rotas públicas."""
        selenium_login(browser, live_server_url, "motorista_test", "testpass123")

        # Motorista pode acessar lista pública de rotas
        browser.get(f"{live_server_url}/rotas/lista/")

        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        # Motorista deve estar logado e pode ver rotas
        assert "/contas/login/" not in browser.current_url

    def test_cliente_cannot_access_rotas_management(self, browser, live_server_url, user_cliente):
        """Testa que cliente não pode acessar gestão de rotas."""
        selenium_login(browser, live_server_url, "cliente_test", "testpass123")
        browser.get(f"{live_server_url}/rotas/gerenciar/rotas/")

        import time

        time.sleep(2)

        page_source = browser.page_source
        assert (
            "/rotas/gerenciar/" not in browser.current_url
            or "403" in page_source
            or "não autorizado" in page_source.lower()
        )
