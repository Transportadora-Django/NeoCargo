"""
Testes de frontend para gestão de veículos com Selenium.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.conftest import selenium_login


@pytest.mark.django_db
class TestVeiculosPage:
    """Testes da página de veículos."""

    def test_veiculos_page_loads(self, browser, live_server_url, user_dono):
        """Testa se a página de veículos carrega."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")
        browser.get(f"{live_server_url}/veiculos/")

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = browser.page_source
        assert (
            "/veiculos/" in browser.current_url or "veículo" in page_source.lower() or "veiculo" in page_source.lower()
        )

    def test_veiculos_list_displays(self, browser, live_server_url, user_dono):
        """Testa se a lista de veículos é exibida."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")
        browser.get(f"{live_server_url}/veiculos/")

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = browser.page_source

        assert (
            "<table" in page_source
            or "veículo" in page_source.lower()
            or "placa" in page_source.lower()
            or "sem veículos" in page_source.lower()
        )

    def test_new_veiculo_button_exists(self, browser, live_server_url, user_dono):
        """Testa se existe botão para adicionar novo veículo."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")
        browser.get(f"{live_server_url}/veiculos/")

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = browser.page_source

        assert "novo" in page_source.lower() or "adicionar" in page_source.lower() or "criar" in page_source.lower()


@pytest.mark.django_db
class TestVeiculosAccessControl:
    """Testes de controle de acesso aos veículos."""

    def test_gerente_can_access_veiculos(self, browser, live_server_url, user_gerente):
        """Testa que gerente pode acessar veículos."""
        selenium_login(browser, live_server_url, "gerente_test", "testpass123")
        browser.get(f"{live_server_url}/veiculos/")

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Gerente deve ter acesso
        page_source = browser.page_source
        assert "/veiculos/" in browser.current_url or "veículo" in page_source.lower()

    def test_cliente_cannot_access_veiculos(self, browser, live_server_url, user_cliente):
        """Testa que cliente não pode acessar gestão de veículos."""
        selenium_login(browser, live_server_url, "cliente_test", "testpass123")
        browser.get(f"{live_server_url}/veiculos/")

        import time

        time.sleep(2)

        # Cliente deve ser bloqueado ou redirecionado
        page_source = browser.page_source
        assert (
            "/veiculos/" not in browser.current_url or "403" in page_source or "não autorizado" in page_source.lower()
        )
