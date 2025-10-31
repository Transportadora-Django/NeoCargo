"""
Configuração adicional do pytest para testes de Selenium.

Este arquivo configura marcadores personalizados e opções específicas
para testes de frontend.
"""


def pytest_configure(config):
    """
    Registra marcadores personalizados para pytest.
    """
    config.addinivalue_line(
        "markers",
        "selenium: marca testes que usam Selenium (deselect with '-m \"not selenium\"')",
    )
    config.addinivalue_line(
        "markers",
        "slow: marca testes lentos que podem ser pulados em CI rápido",
    )
    config.addinivalue_line(
        "markers",
        "frontend: marca testes de frontend/UI",
    )


# Configuração para rodar o live server do Django nos testes do Selenium
pytest_plugins = ["django"]
