from dotenv import load_dotenv
from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import logging, os, time
import pandas as pd

def get_analytics(logger, wait: WebDriverWait, index: int):
    tweet = find_web_element(logger, wait, f"(//article[contains(@data-testid, 'tweet')])[{index}]")

    username = get_username(tweet)

    date = get_date(tweet)

    text = get_text(tweet)

    replies = get_replies(tweet)

    retweets = get_retweets(tweet)

    likes = get_likes(tweet)

    views = get_views(tweet)

    link = get_url(tweet, username)

    data = [{
        'username': username,
        'date': date,
        'text': text,
        'replies': replies,
        'retweets': retweets,
        'likes': likes,
        'views': views,
        'url': link
    }]

    return data

def get_date(parent: WebElement) -> str:
    date_wrapper = parent.find_element(By.XPATH, f".//a[contains(@role, 'link')]/time")
    date = str(date_wrapper.get_attribute("datetime"))

    return date

def get_likes(parent: WebElement) -> str:
    likes = parent.find_element(By.XPATH, ".//button[contains(@data-testid, 'like')]").text

    return likes

def get_replies(parent: WebElement) -> str:
    replies = parent.find_element(By.XPATH, ".//button[contains(@data-testid, 'reply')]").text

    return replies

def get_retweets(parent: WebElement) -> str:
    retweets = parent.find_element(By.XPATH, ".//button[contains(@data-testid, 'retweet')]").text

    return retweets

def get_text(parent: WebElement) -> str:
    try:
        text = parent.find_element(By.XPATH, ".//div[contains(@data-testid, 'tweetText')]").text
    except NoSuchElementException:
        text = ""

    return text

def get_url(parent: WebElement, username: str) -> str:
    partial_link = parent.find_element(By.XPATH, f".//a[starts-with(@href, '/{username[1:]}/status/')]")
    link = partial_link.get_attribute("href")

    return link

def get_username(parent: WebElement) -> str:
    username_wrapper = parent.find_element(By.XPATH, ".//div[contains(@data-testid, 'User-Name')]")
    username = username_wrapper.find_element(By.XPATH, ".//span[starts-with(text(), '@')]").text

    return username

def get_views(parent: WebElement) -> str:
    views = parent.find_element(By.XPATH, "(.//span[contains(@data-testid, 'app-text-transition-container')])[4]").text

    return views

def log():
    log_folder = __DIR__ / 'log/'
    log_folder.mkdir(parents=True, exist_ok=True)
    log_file = log_folder / 'harvest.log'

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger

def find_web_element(logger, wait: WebDriverWait, xpath: str, relative_xpath: str = "") -> WebElement | None:
    wait = wait
    element: WebElement

    try:
        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
        logger.debug(f"TimeoutException for {xpath}! Using relative xpath {relative_xpath}.")
        element = wait.until(EC.presence_of_element_located((By.XPATH, relative_xpath)))
    except ElementClickInterceptedException:
        logger.debug(f"ElementClickInterceptedException for {xpath}! Waiting element to be clickable {relative_xpath}.")
        element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    except ElementNotInteractableException:
        logger.debug(f"ElementNotInteractableException for {xpath}! Waiting element to be clickable {relative_xpath}.")
        element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    finally:
        return element

def start_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=800,600")
    options.add_argument("--log-level=3")

    driver = webdriver.Edge(options=options)

    wait = WebDriverWait(driver, 10)

    return driver, wait

def get_credentials():
    load_dotenv()

    username = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")
    query = os.getenv("QUERY")

    return username, password, query

def login():
    username, password, query = get_credentials()
    browser, wait = start_browser()
    logger = log()

    ac = ActionChains(browser)
    url = "https://x.com/i/flow/login"

    browser.get(url)
    
    user_input_field = find_web_element(logger, wait, '//input[contains(@autocomplete, "username")]', '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')
    user_input_field.send_keys(username)

    advance_btn = find_web_element(logger, wait, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]')
    advance_btn.click()

    ac.send_keys(username)
    ac.key_down(Keys.ENTER)

    time.sleep(2)

    password_input_field = find_web_element(logger, wait, '//input[contains(@type, "password")]', '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')
    password_input_field.send_keys(password)

    login_btn = find_web_element(logger, wait, '//button[contains(@data-testid, "LoginForm_Login_Button")]', '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button')
    login_btn.click()

    return browser, logger, query, wait

# =================================================

__DIR__ = Path(__file__).resolve().parent
files_folder = __DIR__ / "files/"
files_folder.mkdir(parents=True, exist_ok=True)
index = 1
browser, logger, query, wait = login()

time.sleep(2)

browser.get(query)

time.sleep(2)

tweet_analyitics = get_analytics(logger, wait, index)

df = pd.DataFrame(tweet_analyitics)
df.to_excel(__DIR__ / "files/data.xlsx", index=False)