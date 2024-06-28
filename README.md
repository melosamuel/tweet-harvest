# TweetHarvest

## Description

**TweetHarvest** is a project dedicated to twitter data scraping using keywords. The goal is to collect data from tweets and replies based on keywords.

## Requirements

- Python 3.11.x

## Installation

1. Clone the repo:
```sh
git clone https://github.com/usuario/TweetHarvest.git
```

## Usage

1. Create and set up a virtual environment:
    ```sh
    python.exe -m venv [the name of your virtual environment]
    /[the name of your venv]/Scripts/activate
    ```

2. Install all required libraries:
```sh
pip install -r requirements.txt
```
3. Set up your .env file by:
    1. Removing the .base extension from the .env.base file inside **src** directory;
    2. Setting up the variables. Your .env file should look like this:
        ```sh
        LOGIN=YOUR_LOGIN
        PASSWORD=YOUR_PASSWORD
        QUERY=Link for the tweet, profile or keyword.
        ```
4. Run all tests to make sure everything is ok:
    ```sh
    pytest -v
    ```
5. Run harvest.py

### What's the "QUERY" variable?

You can search for people, tweets or retweets it's the link. A tweet's link looks like this: ```https://x.com/[the username]/status/[the tweet's "id"]```

If you want to search for tweets using specific filters, you can use the "search" button, add your filters on "Advanced Search", copy the generated link and paste it in the "QUERY" variable.

## Contributions

Please, feel free to pull request or post an issue!