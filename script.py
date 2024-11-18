import requests
from bs4 import BeautifulSoup
import os
from groq import Groq
from dotenv import load_dotenv
import tweepy

# URL of the main page to scrape
main_url = 'https://www.whitehouse.gov/briefing-room/'

# Headers to mimic a real browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
}

# Function to fetch the most recent article link
def fetch_most_recent_article(url):
    try:
        # Request the main page
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Check for request errors

        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Locate the div with the articles and get the first article
        article_wrapper = soup.find('div', class_='article-wrapper')

        if article_wrapper:
            # Get the most recent article (first one in the list)
            recent_article = article_wrapper.find('article', class_='news-item')
            if recent_article:
                # Extract title, link, and date
                title_tag = recent_article.find('a', class_='news-item__title')
                title = title_tag.get_text(strip=True) if title_tag else "No title"
                link = title_tag['href'] if title_tag else None
                date_tag = recent_article.find('time', class_='posted-on')
                date = date_tag.get_text(strip=True) if date_tag else "No date"

                # Return the article details
                return {
                    'title': title,
                    'link': link,
                    'date': date
                }
        return None

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch main page: {e}")
        return None

# Function to fetch and scrape the content of the article page
def fetch_article_content(article_url):
    try:
        # Request the article page
        response = requests.get(article_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the article page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract content; this might need adjustment based on the actual structure
        content_div = soup.find('div', class_='article-body')
        content = content_div.get_text(separator='\n').strip() if content_div else "Content not found."

        return content

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch article page: {e}")
        return "Error retrieving content."

# saving article and URL
recent_article = fetch_most_recent_article(main_url)
url = recent_article['link']

# Send a GET request to the webpage
response = requests.get(url)
response.raise_for_status()  # Check for request errors

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find the section containing the main content
body_content = soup.find('section', class_='body-content')

# Combine all text within the section into one string
article_content = body_content.get_text(separator=" ", strip=True)

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
            "content": "LL I WANT IS A SUMMARY, DO NOT TELL ME YOU ARE GIVING ME A SUMMARY. Give me a super concise summary of this post. I want you to be non-biased. keep your character count less than 520 characters"
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