# Twitter Thread Automation Script

This script uses Playwright to automate posting entire threads to Twitter, with content sourced from a CSV file.

## Features

-   **Thread Posting**: Automatically posts a main tweet and then adds a series of replies to create a thread.
-   **CSV-driven Content**: Reads thread content from a `threads.csv` file. Each row in the CSV represents a full thread.
-   **Automatic Cookie Management**: On the first run, the script will guide you through a manual login and save your session, so you don't have to log in again.

**Note:** The image posting feature is temporarily disabled while we focus on the threading functionality.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    playwright install
    # On Linux, you may need to install system dependencies:
    # playwright install-deps
    ```

2.  **Prepare Your Thread Content:**
    -   Edit the `threads.csv` file to include the threads you want to post.
    -   The file must have a header row. The required column is `main_tweet`.
    -   You can add any number of comment columns, named sequentially: `comment1`, `comment2`, `comment3`, and so on.
    -   Each row will be posted as a separate thread.

    **Example `threads.csv`:**
    ```csv
    main_tweet,comment1,comment2
    "This is the main tweet of my first thread.", "This is the first reply, expanding on the topic.", "This is the second reply, with a concluding thought."
    "Here's another thread, starting with this tweet.", "It only has one reply.",
    ```

## How to Run

1.  **First Run (Login):**
    -   Run the script: `python post_on_twitter.py`
    -   A browser window will open. Please log in to your Twitter account.
    -   The script will detect when you've logged in, save your session, and then start posting the threads.

2.  **Subsequent Runs:**
    -   Simply run the script again: `python post_on_twitter.py`
    -   It will use the saved `twitter_cookies.json` to log in automatically and post your threads from the CSV.

## File Structure

```
.
├── post_on_twitter.py      # The main script
├── threads.csv             # Your list of threads
├── requirements.txt        # Python dependencies
└── twitter_cookies.json    # Created automatically after the first login
```
