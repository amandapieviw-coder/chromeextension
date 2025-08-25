# Twitter Automation Script

This script uses Playwright to automate posting tweets from a CSV file, complete with an image and automatic session management.

## Features

-   **Automatic Cookie Management**: On the first run, the script will open a browser for you to log in. After a successful login, it saves your session cookies to `twitter_cookies.json`, so you don't have to log in again.
-   **CSV-driven Content**: Reads tweets from a `tweets.csv` file.
-   **Image Posting**: Attaches a single image (`image.jpg`) to every tweet posted.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    playwright install
    # On Linux, you may need to install system dependencies:
    # playwright install-deps
    ```

2.  **Prepare Your Content:**
    -   **Tweets**: Edit the `tweets.csv` file to include the tweets you want to post. It should have a single column with the header `tweet_text`.
    -   **Image**: Place the image you want to post in the same directory as the script and name it `image.jpg`. If this file is not found, a dummy placeholder will be created.

## How to Run

1.  **First Run (Login):**
    -   Run the script: `python post_on_twitter.py`
    -   A browser window will open. Please log in to your Twitter account.
    -   The script will detect when you've logged in, save your session, and then start posting the tweets.

2.  **Subsequent Runs:**
    -   Simply run the script again: `python post_on_twitter.py`
    -   It will use the saved `twitter_cookies.json` to log in automatically and post your tweets.

## File Structure

```
.
├── post_on_twitter.py      # The main script
├── tweets.csv              # Your list of tweets
├── image.jpg               # The image to be posted with each tweet
├── requirements.txt        # Python dependencies
└── twitter_cookies.json    # Created automatically after the first login
```
