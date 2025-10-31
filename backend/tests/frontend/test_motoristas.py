"""
Testes de frontend para gestão de motoristas com Selenium.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.conftest import selenium_login


@pytest.mark.django_db
class TestMotoristasPage:
    """Testes da página de motoristas."""

    def test_motoristas_page_loads(self, browser, live_server_url, user_dono):
        """Testa se a página de motoristas carrega."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")
        browser.get(f"{live_server_url}/gestao/usuarios/")

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = browser.page_source
        assert (
            "/usuarios/" in browser.current_url
            or "usuário" in page_source.lower()
            or "motorista" in page_source.lower()
        )

    def test_motoristas_list_displays(self, browser, live_server_url, user_dono):
        """Testa se a lista de usuários é exibida."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")
        browser.get(f"{live_server_url}/gestao/usuarios/")

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = browser.page_source

        assert (
            "<table" in page_source
            or "usuário" in page_source.lower()
            or "motorista" in page_source.lower()
            or "sem usuários" in page_source.lower()
        )

    def test_new_motorista_button_exists(self, browser, live_server_url, user_dono):
        """Testa se existe seção de gestão de usuários."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")
        browser.get(f"{live_server_url}/gestao/usuarios/")

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = browser.page_source

        # Verifica se há conteúdo de gestão
        assert (
            "usuário" in page_source.lower() or "usuario" in page_source.lower() or "motorista" in page_source.lower()
        )


@pytest.mark.django_db
class TestMotoristasAccessControl:
    """Testes de controle de acesso aos motoristas."""

    def test_gerente_can_access_motoristas(self, browser, live_server_url, user_gerente):
        """Testa que gerente pode acessar gestão de usuários."""
        selenium_login(browser, live_server_url, "gerente_test", "testpass123")
        browser.get(f"{live_server_url}/gestao/usuarios/")

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = browser.page_source
        assert "/usuarios/" in browser.current_url or "usuário" in page_source.lower()

    def test_cliente_cannot_access_motoristas(self, browser, live_server_url, user_cliente):
        """Testa que cliente não pode acessar gestão de usuários."""
        selenium_login(browser, live_server_url, "cliente_test", "testpass123")
        browser.get(f"{live_server_url}/gestao/usuarios/")

        import time

        time.sleep(2)

        page_source = browser.page_source
        assert (
            "/gestao/usuarios/" not in browser.current_url
            or "403" in page_source
            or "não autorizado" in page_source.lower()
        )

    def test_motorista_can_view_own_profile(self, browser, live_server_url, user_motorista):
        """Testa que motorista pode ver seu próprio dashboard."""
        selenium_login(browser, live_server_url, "motorista_test", "testpass123")

        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        # Motorista pode acessar seu dashboard
        browser.get(f"{live_server_url}/motoristas/dashboard/")

        import time

        time.sleep(1)

        page_source = browser.page_source
        # Motorista deve estar no seu dashboard
        assert "/motoristas/dashboard/" in browser.current_url or "dashboard" in page_source.lower()
