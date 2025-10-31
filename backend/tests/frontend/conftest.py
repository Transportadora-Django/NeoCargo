"""
Fixtures para testes de frontend com Selenium.
"""

import os
import shutil

import pytest
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService


User = get_user_model()


@pytest.fixture
def browser():
    """
    Fixture que fornece uma instância do Chrome/Chromium WebDriver.
    Roda em modo headless para testes automatizados.
    """
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # Detectar binário do Chrome/Chromium automaticamente
    chrome_binary_paths = [
        "/usr/bin/chromium-browser",  # Ubuntu/Debian
        "/usr/bin/chromium",  # Algumas distros
        "/usr/bin/google-chrome",  # Google Chrome
        shutil.which("chromium-browser"),  # PATH
        shutil.which("chromium"),  # PATH
        shutil.which("google-chrome"),  # PATH
    ]

    chrome_binary = None
    for path in chrome_binary_paths:
        if path and os.path.exists(path):
            chrome_binary = path
            break

    if chrome_binary:
        chrome_options.binary_location = chrome_binary

    # Detectar chromedriver automaticamente
    chromedriver_paths = [
        "/usr/bin/chromedriver",
        shutil.which("chromedriver"),
    ]

    chromedriver = None
    for path in chromedriver_paths:
        if path and os.path.exists(path):
            chromedriver = path
            break

    if chromedriver:
        service = ChromeService(executable_path=chromedriver)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        # Deixar o Selenium encontrar o chromedriver automaticamente
        driver = webdriver.Chrome(options=chrome_options)

    driver.implicitly_wait(10)

    yield driver

    driver.quit()


@pytest.fixture
def live_server_url(live_server):
    """
    Fixture que fornece a URL do servidor de testes do Django.
    """
    return live_server.url


@pytest.fixture
def user_dono(db):
    """
    Cria um usuário com role DONO para testes.
    """
    from apps.contas.models import Role

    user = User.objects.create_user(
        username="dono_test",
        email="dono@test.com",
        password="testpass123",
    )
    user.profile.role = Role.OWNER
    user.profile.save()
    return user


@pytest.fixture
def user_gerente(db):
    """
    Cria um usuário com role GERENTE para testes.
    """
    from apps.contas.models import Role

    user = User.objects.create_user(
        username="gerente_test",
        email="gerente@test.com",
        password="testpass123",
    )
    user.profile.role = Role.GERENTE
    user.profile.save()
    return user


@pytest.fixture
def user_cliente(db):
    """
    Cria um usuário com role CLIENTE para testes.
    """
    from apps.contas.models import Role

    user = User.objects.create_user(
        username="cliente_test",
        email="cliente@test.com",
        password="testpass123",
    )
    user.profile.role = Role.CLIENTE
    user.profile.save()
    return user


@pytest.fixture
def user_motorista(db):
    """
    Cria um usuário com role MOTORISTA para testes.
    """
    from apps.contas.models import Role

    user = User.objects.create_user(
        username="motorista_test",
        email="motorista@test.com",
        password="testpass123",
    )
    user.profile.role = Role.MOTORISTA
    user.profile.save()
    return user


def selenium_login(browser, live_server_url, username, password):
    """
    Helper function para realizar login via Selenium.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    browser.get(f"{live_server_url}/contas/login/")

    username_input = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, "username")))
    password_input = browser.find_element(By.NAME, "password")

    username_input.send_keys(username)
    password_input.send_keys(password)

    submit_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()

    # Aguarda redirecionamento após login
    WebDriverWait(browser, 10).until(lambda driver: "/contas/login/" not in driver.current_url)
