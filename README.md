# Twitter Automation Script

This script uses Playwright to automate posting a tweet on Twitter. It requires browser cookies for authentication.

## Setup

1.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Install Playwright browsers:**

    ```bash
    playwright install
    ```
    If you are on Linux, you might need to install system dependencies:
    ```bash
    playwright install-deps
    ```

3.  **Create the cookie file:**

    -   Rename the `twitter_cookies.json.example` file to `twitter_cookies.json`.
    -   You need to get your Twitter cookies to authenticate the script. A simple way to do this is to use a browser extension like **Cookie-Editor**.
    -   Install the extension in your browser (e.g., Chrome, Firefox).
    -   Log in to your Twitter account.
    -   Click the Cookie-Editor extension icon and export your cookies in JSON format.
    -   Paste the exported cookie array into the `twitter_cookies.json` file, replacing the example content. The final structure should be a JSON object with a "cookies" key containing an array of your cookies.

## Running the script

Once you have completed the setup, you can run the script with the following command:

```bash
python post_on_twitter.py
```

The script will launch a browser, log in using your cookies, and post the tweet "Welcome to automation life".
