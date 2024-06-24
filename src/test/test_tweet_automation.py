from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os, pyperclip, pytest, re, time

@pytest.fixture
def find_element(start_browser):
    _, wait = start_browser

    def wrapper(xpath: str, relative_xpath: str = ""):
        try:
            element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException:
            print(f"TimeoutException for {xpath}! Using relative xpath.")
            element = wait.until(EC.presence_of_element_located((By.XPATH, relative_xpath)))
        except ElementClickInterceptedException:
            print("ElementClickInterceptedException! Waiting element to be clickable.")
            element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        except ElementNotInteractableException:
            print("ElementNotInteractableException! Waiting element to be clickable.")
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
def log():
    def wrapper(message: str):
        __DIR__ = Path(__file__).resolve().parent
        log_folder = __DIR__ / 'log/'
        log_folder.mkdir(parents=True, exist_ok=True)

        log_file = log_folder / 'tweet_test_automation.log'

        with open(log_file, 'a') as file:
            file.write(f'{datetime.now()} - {message}\n')
    
    return wrapper

@pytest.fixture
def login(start_browser, get_credentials, find_element):
    username, password = get_credentials
    browser, _ = start_browser

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

@pytest.fixture
def start_browser():
    options = Options()
    '''options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=800,600")'''
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=options)

    wait = WebDriverWait(driver, 5)

    return driver, wait

def test_launch_browser(start_browser):
    browser, _ = start_browser

    assert browser != None, f"Couldn't start the browser."

def test_can_browse(start_browser):
    browser, _ = start_browser
    url = "https://www.google.com/"

    browser.get(url)

    assert browser.current_url == url, f"Browser can't go to {url}"

def test_login(start_browser, find_element, get_credentials):
    username, password = get_credentials
    browser, _ = start_browser
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

    assert browser.current_url == target_url, "Unable to login. Check withou --headless otpion."

def test_can_find_a_tweet(login, find_element):
    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")

    assert tweet != None, f"Can't find a tweet"

def test_get_username(login, find_element, log):
    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")
    username_div = tweet.find_element(By.XPATH, ".//div[contains(@data-testid, 'User-Name')]")
    username = username_div.find_element(By.XPATH, ".//span[starts-with(text(), '@')]")

    message = f'Username : {username.text}'
    log(message)
    
    assert username.text[:1] == "@", f"failed to get username. got {username.text} instead"

def test_get_tweet_text(start_browser, login, find_element, log):
    browser, _ = start_browser
    __DIR__ = Path(__file__).resolve().parent

    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")
    text = tweet.find_element(By.XPATH, ".//div[contains(@data-testid, 'tweetText')]")

    if len(text.text) == 0:
        text = ""

    try:
        browser.save_screenshot(f"{__DIR__}/files/tweet_print.png")
    except Exception as e:
        assert 1==0, f"Failed to take a screenshot: {e}"

    try: 
        with open(f"{__DIR__}/files/tweet_text.txt", 'w', encoding='UTF-8') as file:
            file.write(text.text)
    except Exception as e:
        assert 1 == 0, f"Failed to save the text: {e}"
        
    assert text.text != None, f"Failed to get text. Got {text.text} instead."

def test_get_replies_count(login, find_element, log):
    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")
    replies_count = tweet.find_element(By.XPATH, ".//button[contains(@data-testid, 'reply')]")
    count = 0

    if len(replies_count.text) != 0:
        pattern = r'\d+'
        count = re.search(pattern, replies_count.text)
        count = int(count.group())

    message = f'Replies : {replies_count.text}'
    log(message)
    
    assert isinstance(count, int), f"Failed to extract number of replies. Got {replies_count.text} instead"

def test_get_retweets_count(login, find_element, log):
    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")
    retweets_count = tweet.find_element(By.XPATH, ".//button[contains(@data-testid, 'retweet')]")
    count = 0

    if len(retweets_count.text) != 0:
        pattern = r'\d+'
        count = re.search(pattern, retweets_count.text)
        count = int(count.group())

    message = f'Retweets : {retweets_count.text}'
    log(message)

    assert isinstance(count, int), f"Failed to extract number of retweets. Got {retweets_count} instead"

def test_get_likes_count(login, find_element, log):
    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")
    likes_count = tweet.find_element(By.XPATH, ".//button[contains(@data-testid, 'like')]")
    count = 0

    if len(likes_count.text) != 0:
        pattern = r'\d+'
        count = re.search(pattern, likes_count.text)
        count = int(count.group())

    message = f'Likes : {likes_count.text}'
    log(message)

    assert isinstance(count, int), f"Failed to extract number of likes. Got {likes_count.text} instead."

def test_get_views_count(login, find_element, log):
    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")
    views_count = tweet.find_element(By.XPATH, "(.//span[contains(@data-testid, 'app-text-transition-container')])[4]")
    count = 0

    if len(views_count.text) != 0:
        pattern = r'\d+'
        count = re.search(pattern, views_count.text)
        count = int(count.group())

    message = f'Views : {views_count.text}'
    log(message)

    assert isinstance(count, int), f"Failed to extract number of views. Got {views_count.text} instead"

def test_get_bookmarks_count(login, find_element, log):
    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")
    tweet.click()
    bookmarks_count = tweet.find_element(By.XPATH, ".//button[contains(@data-testid, 'bookmark')]")
    count = 0

    if len(bookmarks_count.text) != 0:
        pattern = r'\d+'
        count = re.search(pattern, bookmarks_count.text)
        count = int(count.group())

    message = f'Bookmarks : {bookmarks_count.text}'
    log(message)

    assert isinstance(count, int), f"Failed to extract number of bookmarks. Got {bookmarks_count.text} instead"

def test_get_date(find_element, log, login):
    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")
    tweet.click()

    date_wrapper = tweet.find_element(By.XPATH, f".//a[contains(@role, 'link')]/time")
    date = str(date_wrapper.get_attribute("datetime"))
    
    message = f'Date : {date}'
    log(message)

    assert len(date) > 0, f"Failed to extract date. Got {date} instead"

def test_get_url(find_element, log, login):
    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")
    username_div = tweet.find_element(By.XPATH, "//div[contains(@data-testid, 'User-Name')]")
    username = username_div.find_element(By.XPATH, ".//span[starts-with(text(), '@')]")

    partial_link = tweet.find_element(By.XPATH, f".//a[starts-with(@href, '/{username.text[1:]}/status/')]")
    link = partial_link.get_attribute("href")

    if len(link) > 0:
        message = f"Link: {link}"
        log(message)

    assert link.startswith("https://x.com/"), f"Failed to get link. Got {link} instead"

def test_can_find_replies(find_element, log, login):
    tweet = find_element("(//article[contains(@data-testid, 'tweet')])[1]")
    username_div = tweet.find_element(By.XPATH, ".//div[contains(@data-testid, 'User-Name')]")
    username = username_div.find_element(By.XPATH, ".//span[starts-with(text(), '@')]")

    partial_link = tweet.find_element(By.XPATH, f".//a[starts-with(@href, '/{username.text[1:]}/status/')]")
    link = partial_link.get_attribute("href")

    tweet.click()

    reply_tweet = find_element("(//article[contains(@data-testid, 'tweet')])[2]")

    reply_username_div = reply_tweet.find_element(By.XPATH, ".//div[contains(@data-testid, 'User-Name')]")
    reply_username = reply_username_div.find_element(By.XPATH, ".//span[starts-with(text(), '@')]")

    reply_partial_link = reply_tweet.find_element(By.XPATH, f".//a[starts-with(@href, '/{reply_username.text[1:]}')]")
    reply_link = reply_partial_link.get_attribute("href")

    message = f"Links: {link} | {reply_link}"
    log(message)

    assert link != reply_link, f"Failed to get the tweet and reply links. Got {link} and {reply_link} instead."

def test_get_quotes_count():
    pass