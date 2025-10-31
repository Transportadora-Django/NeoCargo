"""
Testes de frontend para login e autenticação com Selenium.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.conftest import selenium_login


@pytest.mark.django_db
class TestLoginPage:
    """Testes da página de login."""

    def test_login_page_loads(self, browser, live_server_url):
        """Testa se a página de login carrega corretamente."""
        browser.get(f"{live_server_url}/contas/login/")

        # Verifica se está na página de login
        assert "/contas/login/" in browser.current_url

        # Verifica se o título da página contém "Login"
        assert "NeoCargo" in browser.title or "Login" in browser.title

        # Verifica se os campos de login estão presentes
        username_input = browser.find_element(By.NAME, "username")
        password_input = browser.find_element(By.NAME, "password")
        submit_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")

        assert username_input is not None
        assert password_input is not None
        assert submit_button is not None

    def test_login_success_dono(self, browser, live_server_url, user_dono):
        """Testa login bem-sucedido com usuário DONO."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")

        # Verifica se foi redirecionado para o dashboard
        WebDriverWait(browser, 10).until(
            lambda driver: "/dashboard/" in driver.current_url or "/gestao/dashboard/" in driver.current_url
        )

        assert "/dashboard/" in browser.current_url or "/gestao/dashboard/" in browser.current_url

    def test_login_success_gerente(self, browser, live_server_url, user_gerente):
        """Testa login bem-sucedido com usuário GERENTE."""
        selenium_login(browser, live_server_url, "gerente_test", "testpass123")

        # Verifica se foi redirecionado para o dashboard
        WebDriverWait(browser, 10).until(
            lambda driver: "/dashboard/" in driver.current_url or "/gestao/dashboard/" in driver.current_url
        )

        assert "/dashboard/" in browser.current_url or "/gestao/dashboard/" in browser.current_url

    def test_login_success_cliente(self, browser, live_server_url, user_cliente):
        """Testa login bem-sucedido com usuário CLIENTE."""
        selenium_login(browser, live_server_url, "cliente_test", "testpass123")

        # Verifica se foi redirecionado para alguma página interna
        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        assert "/contas/login/" not in browser.current_url

    def test_login_invalid_credentials(self, browser, live_server_url):
        """Testa login com credenciais inválidas."""
        browser.get(f"{live_server_url}/contas/login/")

        username_input = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        password_input = browser.find_element(By.NAME, "password")

        username_input.send_keys("invalid_user")
        password_input.send_keys("invalid_password")

        submit_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Aguarda um pouco para processar a resposta
        import time

        time.sleep(2)

        # Verifica se permanece na página de login
        assert "/contas/login/" in browser.current_url

        # Verifica se há mensagem de erro (pode variar dependendo da implementação)
        page_text = browser.page_source
        assert (
            "incorret" in page_text.lower()
            or "inválid" in page_text.lower()
            or "erro" in page_text.lower()
            or "error" in page_text.lower()
        )

    def test_login_empty_fields(self, browser, live_server_url):
        """Testa tentativa de login com campos vazios."""
        browser.get(f"{live_server_url}/contas/login/")

        submit_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_button.click()

        # Aguarda um pouco
        import time

        time.sleep(1)

        # Verifica se permanece na página de login (não pode fazer login sem credenciais)
        assert "/contas/login/" in browser.current_url


@pytest.mark.django_db
class TestLogout:
    """Testes de logout."""

    def test_logout_success(self, browser, live_server_url, user_dono):
        """Testa logout bem-sucedido."""
        # Faz login primeiro
        selenium_login(browser, live_server_url, "dono_test", "testpass123")

        # Aguarda redirecionamento
        WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)

        # Navega diretamente para a URL de logout
        browser.get(f"{live_server_url}/contas/logout/")

        # Aguarda um pouco para processar
        import time

        time.sleep(2)

        # Verifica se foi deslogado (redirecionado para login ou home)
        assert (
            "/contas/login/" in browser.current_url
            or browser.current_url == f"{live_server_url}/"
            or browser.current_url == live_server_url
            or browser.current_url == f"{live_server_url}"
        )
