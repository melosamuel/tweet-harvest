from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import pytest

@pytest.fixture
def start_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=800,600")

    driver = webdriver.Chrome(options=options)

    wait = WebDriverWait(driver, 2)

    return driver, wait

def test_launch_browser(start_browser):
    browser, wait = start_browser

    assert browser != None