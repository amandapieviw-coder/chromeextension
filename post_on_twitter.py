import asyncio
import json
import os
import csv
from playwright.async_api import async_playwright, TimeoutError

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(SCRIPT_DIR, 'twitter_cookies.json')
CSV_FILE = os.path.join(SCRIPT_DIR, 'threads.csv')
ERROR_SCREENSHOT_FILE = os.path.join(SCRIPT_DIR, 'error_screenshot.png')


async def get_tweet_url(page):
    """
    After a tweet is posted, finds the 'View' link in the confirmation toast
    and returns the URL of the new tweet.
    """
    try:
        toast = page.locator('[data-testid="toast"]').first
        await toast.wait_for(state='visible', timeout=10000)

        view_link = toast.locator('a[href*="/status/"]')
        href = await view_link.get_attribute('href')
        if href:
            return f"https://twitter.com{href}"
        return None
    except TimeoutError:
        print("Could not find confirmation toast. Cannot get new tweet URL.")
        return None

async def post_new_tweet(page, tweet_text):
    """
    Posts a new tweet from the home timeline.
    """
    print("Waiting for the main tweet textarea...")
    # Use the reliable XPath selector for the main composer.
    textarea_selector = "//div[@contenteditable='true' and contains(@role, 'textbox')]"
    textarea = page.locator(textarea_selector).first
    await textarea.wait_for(state='visible', timeout=30000)
    await textarea.click()
    await textarea.fill(tweet_text)

    print("Clicking the 'Post' button for the new tweet...")
    # Use the data-testid for the post button.
    await page.get_by_test_id("tweetButton").click()

    return await get_tweet_url(page)

async def post_reply(page, reply_text):
    """
    Posts a reply to the tweet currently open on the page.
    """
    print("Waiting for the reply textarea...")
    # The reply textarea has a specific aria-label.
    reply_textarea_selector = "div[aria-label='Tweet your reply']"
    textarea = page.locator(reply_textarea_selector)
    await textarea.wait_for(state='visible', timeout=30000)
    await textarea.click()
    await textarea.fill(reply_text)

    print("Clicking the 'Reply' button...")
    # The reply button also has a data-testid, but we filter by the text "Reply".
    await page.get_by_test_id("tweetButton").filter(has_text="Reply").click()

    return await get_tweet_url(page)

async def post_thread(page, thread_data):
    """
    Posts a full thread (main tweet + comments) to Twitter.
    """
    main_tweet_text = thread_data.get('main_tweet', '')
    if not main_tweet_text:
        print("Skipping thread due to empty main_tweet.")
        return

    print(f"Posting main tweet: '{main_tweet_text}'")
    await page.goto("https://twitter.com/home")
    tweet_url = await post_new_tweet(page, main_tweet_text)

    if not tweet_url:
        print("Failed to get URL of the main tweet. Cannot continue thread.")
        return

    comments = [thread_data.get(f'comment{i}') for i in range(1, 10) if thread_data.get(f'comment{i}')]

    for i, comment_text in enumerate(comments):
        print(f"\nNavigating to previous tweet to reply: {tweet_url}")
        await page.goto(tweet_url)

        print(f"Posting reply {i+1}: '{comment_text}'")
        new_tweet_url = await post_reply(page, comment_text)

        if not new_tweet_url:
            print(f"Failed to get URL of reply {i+1}. Stopping thread here.")
            break
        tweet_url = new_tweet_url # Chain the replies

async def main():
    """
    Launches a browser, handles login, and posts threads from a CSV file.
    """
    success = False
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = None

        # --- Login/Cookie Flow ---
        if os.path.exists(COOKIES_FILE):
            print(f"Found cookie file at {COOKIES_FILE}. Loading session.")
            context = await browser.new_context(storage_state=COOKIES_FILE)
            page = await context.new_page()
            await page.goto('https://twitter.com/home')
            # Verify login by checking for a unique element on the home page, e.g., the "For You" tab
            if not await page.get_by_test_id("ScrollSnap-Home").is_visible(timeout=10000):
                 print("Cookie login failed. Please log in manually.")
                 # If cookie login fails, we fall through to the manual login process
                 await context.close() # Close the failed context
                 context = await browser.new_context()
                 page = await context.new_page()
                 await page.goto('https://twitter.com/login')
            else:
                 print("Cookie login successful.")

        if not context or not await page.get_by_test_id("ScrollSnap-Home").is_visible(timeout=1000):
            if not context: # If context doesn't exist at all
                context = await browser.new_context()
                page = await context.new_page()

            print("Cookie file not found or invalid. Please log in manually.")
            await page.goto('https://twitter.com/login')
            print("Waiting for you to complete login...")
            await page.wait_for_url("https://twitter.com/home", timeout=300000)
            print("Login successful! Saving session to a new cookie file...")
            await context.storage_state(path=COOKIES_FILE)
            print(f"Cookies saved to {COOKIES_FILE}.")

        # --- Main Task ---
        try:
            with open(CSV_FILE, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                threads = list(reader)

            print(f"\nFound {len(threads)} threads to post from {CSV_FILE}.")

            for i, thread_data in enumerate(threads):
                print(f"\n--- Posting Thread {i+1}/{len(threads)} ---")
                await post_thread(page, thread_data)

            success = True

        except FileNotFoundError:
            print(f"Error: The CSV file was not found at {CSV_FILE}. Please check the file path.")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            await page.screenshot(path=ERROR_SCREENSHOT_FILE)
            print(f"A screenshot has been saved to '{ERROR_SCREENSHOT_FILE}' for debugging.")
        finally:
            if success:
                print("\nScript finished: All threads processed successfully.")
            else:
                print("\nScript finished with errors.")
            print("Closing browser.")
            await browser.close()

def setup_files():
    if not os.path.exists(CSV_FILE):
        print(f"Warning: CSV file not found. Creating an example at {CSV_FILE}.")
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['main_tweet', 'comment1', 'comment2'])
            writer.writerow(['This is the main tweet of a thread.', 'This is the first reply.', 'This is the second reply.'])

if __name__ == '__main__':
    setup_files()
    asyncio.run(main())
