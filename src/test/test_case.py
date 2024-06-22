from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os, pytest, re, time

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
def login(start_browser, get_credentials, find_element):
    username, password = get_credentials
    browser, wait = start_browser

    ac = ActionChains(browser)
    url = "https://x.com/i/flow/login"

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

    return browser, wait


@pytest.fixture
def start_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=800,600")
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=options)

    wait = WebDriverWait(driver, 5)

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

def test_can_find_a_tweet(login, find_element):
    browser, wait = login

    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")

    assert tweet != None

def test_extract_username(login, find_element):
    browser, wait = login

    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")
    username_div = tweet.find_element(By.XPATH, "//div[contains(@data-testid, 'User-Name')]")
    username = username_div.find_element(By.XPATH, ".//span[starts-with(text(), '@')]")
    
    assert username.text[:1] == "@", f"username: {username.text}"

def test_extract_tweet_text(login, find_element):
    browser, wait = login

    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")
    text = tweet.find_element(By.XPATH, ".//div[contains(@data-testid, 'tweetText')]")

    try:
        browser.save_screenshot("./tweet_text.png")
    except Exception as e:
        assert 1==0, f"Failed to take a screenshot: {e}"

    try: 
        with open("./tweet_text.txt", 'w', encoding='UTF-8') as file:
            file.write(text.text)
    except Exception as e:
        assert 1 == 0, f"Failed to write the text: {e}"
        
    assert text.text != None, f"text: {text.text}"

def test_get_replies_count(login, find_element):
    browser, wait = login

    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")
    replies_wrapper = tweet.find_element(By.XPATH, ".//button[contains(@data-testid, 'reply')]")
    replies_count = replies_wrapper.find_element(By.XPATH, ".//span[contains(@data-testid, 'app-text-transition-container')]")

    pattern = r'\d+'
    count = re.search(pattern, replies_count.text)
    count = int(count.group())

    assert isinstance(count, int), f"Failed to extract number of replies. Got {replies_count.text} instead"


@pytest.mark.skip(reason="Not implemented yet!")
def test_get_retweets_count():
    pass

@pytest.mark.skip(reason="Not implemented yet!")
def test_get_quotes_count():
    pass

def test_get_likes_count(login, find_element):
    browser, wait = login

    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")
    likes_wrapper = tweet.find_element(By.XPATH, ".//button[contains(@data-testid, 'like')]")
    likes_count = likes_wrapper.find_element(By.XPATH, ".//span[contains(@data-testid, 'app-text-transition-container')]")

    pattern = r'\d+'
    count = re.search(pattern, likes_count.text)
    count = int(count.group())

    assert isinstance(count, int), f"Failed to extract number of replies. Got {likes_count.text} instead"


@pytest.mark.skip(reason="Not implemented yet!")
def test_get_views_count():
    pass

@pytest.mark.skip(reason="Not implemented yet!")
def test_can_find_replies():
    pass

@pytest.mark.skip(reason="Not implemented yet!")
def test_extract_tweet_url():
    pass