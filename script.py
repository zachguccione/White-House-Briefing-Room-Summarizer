import requests
from bs4 import BeautifulSoup
import pprint as pp
import os
from groq import Groq
from dotenv import load_dotenv

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

recent_article = fetch_most_recent_article(main_url)
print(recent_article)

# URL of the specific article page
article_url = recent_article['link']

# Headers to mimic a real browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
}

# Function to fetch and parse the article content
def fetch_article_body_content(url):
    try:
        # Request the article page
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Check for request errors

        # Parse the article page HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Locate the <article> tag with the specific class
        article = soup.find('article', class_='post-108981 post type-post status-publish hentry category-speeches-remarks')

        # Find the <section class="body-content"> within the <article> tag
        body_content_section = article.find('section', class_='body-content') if article else None

        if body_content_section:
            # Extract and combine all text within the <section> into a single string
            content = ' '.join([p.get_text(strip=True) for p in body_content_section.find_all('p')])
            return content
        else:
            return "Content not found in the specified section."

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch article page: {e}")
        return "Error retrieving content."

# Fetch the content of the article body and print
article_content = fetch_article_body_content(article_url)
print(article_content)

# Initialize the client with the API key
load_dotenv("keys.env")
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Define the chat completion request using client.chat.completions.create()
chat_completion = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {
            "role": "system",
            "content": "You are a non-partisan and non-biased bot attempting to give information to the general population. You are to limit your response to 560 characters."
        },
        {
            "role": "user",
            "content": article_content
        }
    ]
)

# Print the response content
response = chat_completion.choices[0].message.content

title = recent_article['title']
link = recent_article['link']

pp.pprint(recent_article['title'])
pp.pprint(recent_article['link'])
pp.pprint(response)