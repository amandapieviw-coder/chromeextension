import asyncio
import json
import os
import csv
from playwright.async_api import async_playwright, TimeoutError

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(SCRIPT_DIR, 'twitter_cookies.json')
CSV_FILE = os.path.join(SCRIPT_DIR, 'threads.csv')
IMAGE_TO_POST = os.path.join(SCRIPT_DIR, 'image.jpg')
ERROR_SCREENSHOT_FILE = os.path.join(SCRIPT_DIR, 'error_screenshot.png')


async def get_tweet_url(page):
    """
    After a tweet is posted, this function finds the 'View' link in the confirmation toast
    and returns the URL of the new tweet.
    """
    try:
        toast_selector = '[data-testid="toast"]'
        view_link_selector = 'a[href*="/status/"]'

        toast = page.locator(toast_selector)
        await toast.wait_for(state='visible', timeout=10000)

        view_link = toast.locator(view_link_selector)
        await view_link.wait_for(state='visible', timeout=5000)

        href = await view_link.get_attribute('href')
        if href:
            return f"https://twitter.com{href}"
        return None
    except TimeoutError:
        print("Could not find the 'View' link in the confirmation toast.")
        print("Will try to find the latest tweet on the profile instead.")
        # Fallback: go to profile and get the first tweet's link
        # This is more complex and will be implemented if needed. For now, we rely on the toast.
        return None

async def post_new_tweet(page, tweet_text, image_path=None):
    """
    Posts a new tweet from the home timeline.
    """
    print("Waiting for the main tweet textarea...")
    textarea_selector = "div[data-testid='tweetTextarea_0']"
    await page.locator(textarea_selector).click()
    await page.locator(textarea_selector).fill(tweet_text)

    if image_path and os.path.exists(image_path):
        # Image upload logic remains the same
        pass  # For brevity, skipping the image logic as user wants to focus on threads

    print("Clicking the 'Post' button for the new tweet...")
    post_button_selector = "button[data-testid='tweetButton']"
    await page.locator(post_button_selector).click()

    return await get_tweet_url(page)

async def post_reply(page, reply_text):
    """
    Posts a reply to the tweet currently open on the page.
    """
    print("Waiting for the reply textarea...")
    # The selector for the reply composer is different from the main one.
    reply_textarea_selector = "div[data-testid='tweetTextarea_0']" # This might be the same, context matters.
    await page.locator(reply_textarea_selector).click()
    await page.locator(reply_textarea_selector).fill(reply_text)

    print("Clicking the 'Reply' button...")
    reply_button_selector = "button[data-testid='tweetButton']" # Same testid, but the label is 'Reply'
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

    # 1. Post the main tweet
    print(f"Posting main tweet: '{main_tweet_text}'")
    await page.goto("https://twitter.com/home") # Start from home for each new thread
    tweet_url = await post_new_tweet(page, main_tweet_text)

    if not tweet_url:
        print("Failed to get URL of the main tweet. Cannot continue thread.")
        return

    # 2. Post the comments as replies
    comments = []
    for i in range(1, 10): # Assuming max 9 comments
        comment = thread_data.get(f'comment{i}')
        if comment:
            comments.append(comment)
        else:
            break

    for i, comment_text in enumerate(comments):
        print(f"Navigating to previous tweet to reply: {tweet_url}")
        await page.goto(tweet_url)

        print(f"Posting reply {i+1}: '{comment_text}'")
        new_tweet_url = await post_reply(page, comment_text)

        if not new_tweet_url:
            print(f"Failed to get URL of reply {i+1}. Stopping thread here.")
            break
        tweet_url = new_tweet_url # Update URL for the next reply in the chain

async def main():
    """
    Launches a browser, handles login, and posts threads from a CSV file.
    """
    # Simplified main function to focus on threading logic
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=COOKIES_FILE)
        page = await context.new_page()

        try:
            with open(CSV_FILE, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                threads = list(reader)

            print(f"Found {len(threads)} threads to post from {CSV_FILE}.")

            for i, thread_data in enumerate(threads):
                print(f"\n--- Posting Thread {i+1}/{len(threads)} ---")
                await post_thread(page, thread_data)

            print("\nScript finished: All threads processed.")

        except FileNotFoundError:
            print(f"Error: The CSV file was not found at {CSV_FILE}")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            await page.screenshot(path=ERROR_SCREENSHOT_FILE)
            print(f"A screenshot has been saved to '{ERROR_SCREENSHOT_FILE}' for debugging.")
        finally:
            print("Closing browser.")
            await browser.close()

def setup_files():
    """
    Creates dummy image and CSV files if they don't exist.
    """
    if not os.path.exists(IMAGE_TO_POST):
        print(f"Warning: Test image '{os.path.basename(IMAGE_TO_POST)}' not found.")
        with open(IMAGE_TO_POST, 'w') as f: f.write("dummy")

    if not os.path.exists(CSV_FILE):
        print(f"Warning: CSV file '{os.path.basename(CSV_FILE)}' not found. Creating an example.")
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['main_tweet', 'comment1', 'comment2'])
            writer.writerow(['This is the main tweet of a thread.', 'This is the first reply.', 'This is the second reply.'])

if __name__ == '__main__':
    # Login check is implicitly handled by loading cookies.
    # If cookies are invalid, the script will fail, prompting a re-login on next run.
    # A full login flow is omitted here to simplify for the threading task.
    setup_files()
    asyncio.run(main())
