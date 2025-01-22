import requests
from bs4 import BeautifulSoup
import os
from groq import Groq
from dotenv import load_dotenv
import tweepy

# URL of the main page to scrape
main_url = 'https://www.whitehouse.gov/presidential-actions/'

# Headers to mimic a real browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
}

import requests
from bs4 import BeautifulSoup

def fetch_most_recent_article(url):
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    posts_container = soup.find("ul", class_="wp-block-post-template")
    if not posts_container:
        return None
    
    posts = posts_container.find_all("li", recursive=False)
    if not posts:
        return None
    
    most_recent_post = posts[0]
    
    title_tag = most_recent_post.find("h2", class_="wp-block-post-title")
    if not title_tag:
        return None
    
    link_tag = title_tag.find("a")
    if not link_tag:
        return None
    
    title_text = link_tag.get_text(strip=True)
    link_url   = link_tag.get("href")
    
    time_tag = most_recent_post.find("time")
    if time_tag:
        datetime_value = time_tag.get("datetime")
        date_text      = time_tag.get_text(strip=True)
    else:
        datetime_value = None
        date_text      = None
    
    return {
        "title": title_text,
        "link": link_url,
        "datetime": datetime_value,  
        "date": date_text            
    }

def fetch_article_content(url):
    response = requests.get(url)
    response.raise_for_status()  # Raises HTTPError if the request resulted in an error
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    content_div = soup.find(
        "div", 
        class_="entry-content wp-block-post-content has-global-padding is-layout-constrained wp-block-post-content-is-layout-constrained"
    )
    
    if content_div:
        article_text = content_div.get_text(separator="\n", strip=True)
        return article_text
    
    return None

recent_article = fetch_most_recent_article(main_url)
url = recent_article['link']

article_content = fetch_article_content(url)

response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'html.parser')

body_content = soup.find('section', class_='body-content')

# Initialize the client with the API key
load_dotenv("keys.env")
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)

# Define the chat completion request using client.chat.completions.create()
chat_completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": "ALL I WANT IS A SUMMARY, DO NOT TELL ME YOU ARE GIVING ME A SUMMARY. Give me a super concise summary of this post. I want you to be non-biased. keep your character count less than 520 characters"
        },
        {
            "role": "user",
            "content": article_content
        }
    ]
)

# Print the response content
response = chat_completion.choices[0].message.content

# Creating variables of link and title
title = recent_article['title']
link = recent_article['link']

# Function to split text into 280-character parts
def split_into_tweets(text, max_length=280):
    words = text.split()
    tweets = []
    tweet = ""
    
    for word in words:
        if len(tweet) + len(word) + 1 > max_length:
            tweets.append(tweet)
            tweet = word
        else:
            tweet += " " + word if tweet else word
    
    if tweet:
        tweets.append(tweet)
    
    return tweets

# Creating Tweet
tweet_content = split_into_tweets(response)
tweets = tweet_content
tweets.insert(0, title)
# tweets.append("#news #whitehouse #biden #trump #update")

# function to write to our text file
def write_to_file(filename, text):
    try:
        with open(filename, 'w') as f:
            f.write(text)
        print(f"Successfully wrote to {filename}")
    except:
        print("Failed")

# read our text file:
def read_file_as_string(file_path):
    with open(file_path, "r") as file:
        return file.read()
    
last_article_tweeted = read_file_as_string("last_article_tweeted.txt")

# thread
def create_thread(tweets):
    first_tweet = tweepy_client.create_tweet(text=tweets[0])
    reply_to_id = first_tweet

    for tweet in tweets[1:]:
        reply_to_id = tweepy_client.create_tweet(text=tweet, in_reply_to_tweet_id=first_tweet.data['id'])


# Twitter API credentials from .env file
API_KEY = os.getenv("API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("CLIENT_ID")
ACCESS_TOKEN_SECRET = os.getenv("CLIENT_SECRET")

if last_article_tweeted != url:
    tweepy_client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET_KEY,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    # create the tweet
    try:
        create_thread(tweets=tweets)
        last_article_tweeted = tweets[0]
        write_to_file("last_article_tweeted.txt", url)
    except tweepy.TweepyException as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}") 
else:
    print("No new articles")