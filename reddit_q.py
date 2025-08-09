import requests
from os.path import isfile
from datetime import datetime
import json
import time
import praw  # Optional for full post data
import requests
from bs4 import BeautifulSoup
import pickle as pkl
# Optional: Reddit API credentials (for fetching full post data)
USE_PRAW = True  # Set True if you want to enrich results using PRAW
REDDIT_CLIENT_ID = 'XF9l_UXAJChILPdGA'
REDDIT_CLIENT_SECRET = 'BGYw0-'
REDDIT_USER_AGENT = 'Specialist--3777'
reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
# Set up your credentials


def fetch_reddit_comments(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; RedditScraper/1.0)'
    }

    # Make sure it's the old.reddit format (easier to parse)
    if not url.startswith("https://old.reddit.com"):
        url = url.replace("https://www.reddit.com", "https://old.reddit.com")

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    comments = []
    comment_divs = soup.find_all("div", class_="entry")

    for div in comment_divs:
        author = div.find("a", class_="author")
        content = div.find("div", class_="md")
        if author and content:
            comments.append({
                "author": author.text,
                "comment": content.text.strip()
            })

    return comments

# Example usage
if __name__ == "__main__":

    subr = "learnprogramming"
    if isfile(subr):
        sub_ursl=pkl.load(subr)
    else:
        subreddit = reddit.subreddit(subr)
        query = "python"
        result = subreddit.search(query, limit=10)
        sub_ursl = [s.url for s in result]
        with open(subr,'wb') as f:
            pkl.dump(sub_ursl,f)
    
    for url in sub_ursl:
        # print(f"{submission.title} ({submission.score} points)")
        # print(submission.url)
        # print("---")
        comments = fetch_reddit_comments(url)

        for idx, c in enumerate(comments, 1):
            print(f"{idx}. {c['author']}: {c['comment']}\n")
