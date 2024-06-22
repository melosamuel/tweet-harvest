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
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=options)

    wait = WebDriverWait(driver, 2)

    return driver, wait

def test_launch_browser(start_browser):
    browser, wait = start_browser

    assert browser != None

def test_can_browse(start_browser):
    browser, wait = start_browser
    url = "https://www.google.com/"

    browser.get(url)

    assert browser.current_url == url

@pytest.mark.skip(reason="Not implemented yet!")
def test_login():
    pass

@pytest.mark.skip(reason="Not implemented yet!")
def test_can_find_a_tweet():
    pass

@pytest.mark.skip(reason="Not implemented yet!")
def test_exctract_username():
    pass

@pytest.mark.skip(reason="Not implemented yet!")
def test_exctract_tweet_text():
    pass

@pytest.mark.skip(reason="Not implemented yet!")
def test_exctrat_numbers():
    pass

@pytest.mark.skip(reason="Not implemented yet!")
def test_can_find_replies():
    pass

@pytest.mark.skip(reason="Not implemented yet!")
def test_exctract_tweet_url():
    pass