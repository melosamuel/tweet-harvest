from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os, pytest, time

@pytest.fixture
def find_element(start_browser):
    browser, wait = start_browser

    def wrapper(xpath: str, relative_xpath: str = ""):
        try:
            element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException:
            print(f"TimeoutException for {xpath}! Using relative xpath.")
            element = wait.until(EC.presence_of_element_located((By.XPATH, relative_xpath)))
        except ElementClickInterceptedException:
            print("ElementClickInterceptedException! Waiting for element to be clickable.")
            element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        finally:
            return element

    return wrapper

@pytest.fixture
def get_credentials():
    load_dotenv()

    username = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")

    return username, password

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

def test_login(start_browser, find_element, get_credentials):
    username, password = get_credentials
    browser, wait = start_browser
    ac = ActionChains(browser)
    url = "https://x.com/i/flow/login"
    target_url = "https://x.com/home"

    browser.get(url)
    
    user_input_field = find_element('//input[contains(@autocomplete, "username")]', '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')
    user_input_field.send_keys(username)

    advance_btn = find_element('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]')
    advance_btn.click()

    ac.send_keys(username)
    ac.key_down(Keys.ENTER)

    password_input_field = find_element('//input[contains(@type, "password")]', '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')
    password_input_field.send_keys(password)

    login_btn = find_element('//button[contains(@data-testid, "LoginForm_Login_Button")]', '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button')
    login_btn.click()

    time.sleep(5)

    assert browser.current_url == target_url

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