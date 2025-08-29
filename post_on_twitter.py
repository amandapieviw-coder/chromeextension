import asyncio
import json
import os
import csv
from playwright.async_api import async_playwright

# --- Configuration ---
# Get the absolute path of the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define file paths relative to the script's directory
COOKIES_FILE = os.path.join(SCRIPT_DIR, 'twitter_cookies.json')
CSV_FILE = os.path.join(SCRIPT_DIR, 'tweets.csv')
IMAGE_TO_POST = os.path.join(SCRIPT_DIR, 'image.jpg')
ERROR_SCREENSHOT_FILE = os.path.join(SCRIPT_DIR, 'error_screenshot.png')


async def post_tweet(page, tweet_text, image_path=None):
    """
    Posts a tweet with the given text and optionally an image.
    """
    print("Waiting for the tweet textarea...")
    textarea_selector = "//div[@contenteditable='true' and contains(@role, 'textbox')]"
    await page.wait_for_selector(textarea_selector, timeout=60000)

    print(f"Typing the tweet: '{tweet_text}'")
    await page.locator(textarea_selector).fill(tweet_text)

    if image_path and os.path.exists(image_path):
        try:
            print(f"Uploading image: {image_path}")
            add_image_button_selector = '[aria-label="Add photos or video"]'

            async with page.expect_file_chooser() as fc_info:
                await page.locator(add_image_button_selector).click()
            file_chooser = await fc_info.value
            await file_chooser.set_files(image_path)

            await page.locator('[data-testid="tweetPhoto"]').first.wait_for(state='visible', timeout=60000)
            print("Image preview is visible.")
        except Exception as e:
            print(f"Could not upload image: {e}")
            print("Posting tweet without image.")
    elif image_path:
        print(f"Warning: Image not found at '{image_path}'. Posting tweet without image.")

    print("Waiting for the post button...")
    post_button_selector = "//button[@data-testid='tweetButtonInline' and .//span[text()='Post']]"
    post_button = page.locator(post_button_selector)

    print("Clicking the post button...")
    await post_button.click(timeout=60000)

    print("Tweet posted successfully!")
    await page.wait_for_timeout(5000)

async def main():
    """
    Launches a browser, handles login, and posts tweets from a CSV file.
    """
    success = False
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = None

        if os.path.exists(COOKIES_FILE):
            print(f"Loading cookies from {COOKIES_FILE}")
            context = await browser.new_context(storage_state=COOKIES_FILE)
        else:
            print("Cookie file not found. A new one will be created after you log in.")
            context = await browser.new_context()

        page = await context.new_page()

        try:
            print("Navigating to Twitter...")
            await page.goto('https://twitter.com/home', timeout=60000)

            login_button_selector = "a[data-testid='loginButton']"
            is_login_required = await page.is_visible(login_button_selector, timeout=5000)

            if is_login_required:
                print("Login required. Please log in to your Twitter account in the browser window.")
                await page.wait_for_url("https://twitter.com/home", timeout=300000)
                print("Login successful!")
                print(f"Saving authentication state to {COOKIES_FILE}...")
                await context.storage_state(path=COOKIES_FILE)
                print("Cookies saved successfully.")
            else:
                print("Successfully logged in using existing cookies.")

            # --- Process tweets from CSV ---
            with open(CSV_FILE, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                tweets = list(reader)

            print(f"Found {len(tweets)} tweets in {CSV_FILE}.")

            for i, row in enumerate(tweets):
                tweet_text = row.get('tweet_text', '')
                if not tweet_text:
                    print(f"Skipping row {i+1} due to empty tweet_text.")
                    continue

                print(f"\n--- Posting tweet {i+1}/{len(tweets)} ---")
                await post_tweet(page, tweet_text, image_path=IMAGE_TO_POST)

            success = True

        except Exception as e:
            print(f"\nAn error occurred: {e}")
            await page.screenshot(path=ERROR_SCREENSHOT_FILE)
            print(f"A screenshot has been saved to '{ERROR_SCREENSHOT_FILE}' for debugging.")

        finally:
            if success:
                print("\nScript finished: All tweets posted successfully.")
            else:
                print("\nScript finished with errors.")
            print("Closing browser.")
            await browser.close()

def setup_files():
    """
    Creates dummy image and CSV files if they don't exist.
    """
    if not os.path.exists(IMAGE_TO_POST):
        print(f"Warning: Test image '{os.path.basename(IMAGE_TO_POST)}' not found.")
        print("A dummy file will be created. Please replace it with a real image.")
        with open(IMAGE_TO_POST, 'w') as f:
            f.write("This is a dummy file for testing.")

    if not os.path.exists(CSV_FILE):
        print(f"Warning: CSV file '{os.path.basename(CSV_FILE)}' not found.")
        print("An example file will be created with sample tweets.")
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['tweet_text'])
            writer.writerow(['This is a sample tweet from the auto-generated CSV.'])
            writer.writerow(['#TwitterAutomation is fun!'])

if __name__ == '__main__':
    setup_files()
    asyncio.run(main())
