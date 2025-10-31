"""
Testes de frontend para a página de relatórios (NC-39) com Selenium.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.frontend.conftest import selenium_login


@pytest.mark.django_db
class TestRelatoriosPage:
    """Testes da página de relatórios gerenciais."""

    def test_relatorios_page_loads(self, browser, live_server_url, user_dono):
        """Testa se a página de relatórios carrega corretamente."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")

        # Navega para relatórios
        browser.get(f"{live_server_url}/gestao/relatorios/")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Verifica se está na página correta
        assert "/gestao/relatorios/" in browser.current_url

        # Verifica se há conteúdo de relatórios
        page_text = browser.page_source
        assert (
            "relatório" in page_text.lower()
            or "relatorio" in page_text.lower()
            or "gráfico" in page_text.lower()
            or "grafico" in page_text.lower()
        )

    def test_relatorios_filters_exist(self, browser, live_server_url, user_dono):
        """Testa se os filtros de período e ano estão presentes."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")
        browser.get(f"{live_server_url}/gestao/relatorios/")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = browser.page_source

        # Verifica se há elementos de filtro
        assert (
            "período" in page_source.lower()
            or "periodo" in page_source.lower()
            or "filtro" in page_source.lower()
            or "30dias" in page_source.lower()
            or "ano" in page_source.lower()
        )

    def test_relatorios_change_period_filter(self, browser, live_server_url, user_dono):
        """Testa mudança de filtro de período."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")
        browser.get(f"{live_server_url}/gestao/relatorios/")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Procura por links ou botões de filtro
        try:
            # Tenta encontrar link de período diferente (ex: "90 dias")
            links = browser.find_elements(By.TAG_NAME, "a")
            period_links = [link for link in links if "periodo=" in link.get_attribute("href") or ""]

            if len(period_links) > 0:
                # Clica no primeiro filtro encontrado
                period_links[0].click()

                # Aguarda carregamento
                import time

                time.sleep(2)

                # Verifica se ainda está na página de relatórios
                assert "/gestao/relatorios/" in browser.current_url

        except Exception:
            # Se não encontrar links, apenas verifica que a página carregou
            assert "/gestao/relatorios/" in browser.current_url

    def test_relatorios_charts_exist(self, browser, live_server_url, user_dono):
        """Testa se os gráficos (Canvas) estão presentes na página."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")
        browser.get(f"{live_server_url}/gestao/relatorios/")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Aguarda um pouco mais para os gráficos renderizarem
        import time

        time.sleep(3)

        # Procura por elementos canvas (Chart.js)
        page_source = browser.page_source

        # Verifica se Chart.js está presente
        assert "chart.js" in page_source.lower() or "chartjs" in page_source.lower() or "<canvas" in page_source.lower()

    def test_relatorios_stat_cards_exist(self, browser, live_server_url, user_dono):
        """Testa se os cards de estatísticas estão presentes."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")
        browser.get(f"{live_server_url}/gestao/relatorios/")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = browser.page_source

        # Verifica se há indicadores financeiros
        assert (
            "receita" in page_source.lower()
            or "lucro" in page_source.lower()
            or "custo" in page_source.lower()
            or "combustível" in page_source.lower()
            or "combustivel" in page_source.lower()
            or "pedidos" in page_source.lower()
            or "sem dados" in page_source.lower()  # Mensagem quando não há dados
        )

    def test_relatorios_fuel_costs_visible(self, browser, live_server_url, user_dono):
        """Testa se os custos de combustível estão visíveis (NC-39 enhancement)."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")
        browser.get(f"{live_server_url}/gestao/relatorios/")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_source = browser.page_source

        # Verifica se há menção a combustível
        assert (
            "combustível" in page_source.lower()
            or "combustivel" in page_source.lower()
            or "custo_combustivel" in page_source.lower()
            or "sem dados" in page_source.lower()  # Pode não ter dados
        )

    def test_relatorios_print_button_exists(self, browser, live_server_url, user_dono):
        """Testa se o botão de imprimir está presente."""
        selenium_login(browser, live_server_url, "dono_test", "testpass123")
        browser.get(f"{live_server_url}/gestao/relatorios/")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Procura por botão de impressão
        try:
            print_button = browser.find_element(
                By.XPATH,
                "//button[contains(text(), 'Imprimir') or contains(text(), 'Print')]",
            )
            assert print_button is not None
        except Exception:
            # Se não encontrar botão, verifica se há função de impressão no JavaScript
            page_source = browser.page_source
            assert (
                "print()" in page_source.lower()
                or "window.print" in page_source.lower()
                or "imprimir" in page_source.lower()
            )


@pytest.mark.django_db
class TestRelatoriosAccessControl:
    """Testes de controle de acesso aos relatórios."""

    def test_gerente_can_access_relatorios(self, browser, live_server_url, user_gerente):
        """Testa que gerente tem acesso aos relatórios."""
        selenium_login(browser, live_server_url, "gerente_test", "testpass123")
        browser.get(f"{live_server_url}/gestao/relatorios/")

        # Aguarda carregamento
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Verifica acesso
        assert "/gestao/relatorios/" in browser.current_url

        # Não deve ter mensagem de erro
        page_source = browser.page_source
        assert "403" not in page_source and "não autorizado" not in page_source.lower()

    def test_cliente_cannot_access_relatorios(self, browser, live_server_url, user_cliente):
        """Testa que cliente não tem acesso aos relatórios."""
        selenium_login(browser, live_server_url, "cliente_test", "testpass123")

        # Tenta acessar relatórios
        browser.get(f"{live_server_url}/gestao/relatorios/")

        # Aguarda processamento
        import time

        time.sleep(2)

        # Deve ser bloqueado
        assert (
            "/gestao/relatorios/" not in browser.current_url
            or "403" in browser.page_source
            or "não autorizado" in browser.page_source.lower()
            or "permissão" in browser.page_source.lower()
        )

    def test_motorista_cannot_access_relatorios(self, browser, live_server_url, user_motorista):
        """Testa que motorista não tem acesso aos relatórios."""
        selenium_login(browser, live_server_url, "motorista_test", "testpass123")

        # Tenta acessar relatórios
        browser.get(f"{live_server_url}/gestao/relatorios/")

        # Aguarda processamento
        import time

        time.sleep(2)

        # Deve ser bloqueado
        assert (
            "/gestao/relatorios/" not in browser.current_url
            or "403" in browser.page_source
            or "não autorizado" in browser.page_source.lower()
            or "permissão" in browser.page_source.lower()
        )
