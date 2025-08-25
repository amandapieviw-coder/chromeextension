import asyncio
import json
import os
import csv
from playwright.async_api import async_playwright

async def post_tweet(page, tweet_text, image_path=None):
    """
    Posts a tweet with the given text and optionally an image.
    """
    print("Waiting for the tweet textarea...")
    textarea_selector = "//div[@contenteditable='true' and contains(@role, 'textbox')]"
    await page.wait_for_selector(textarea_selector, timeout=60000)

    print(f"Typing the tweet: '{tweet_text}'")
    await page.locator(textarea_selector).fill(tweet_text)

    if image_path:
        if not os.path.exists(image_path):
            print(f"Error: Image not found at '{image_path}'. Posting tweet without image.")
        else:
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
    cookies_file = 'twitter_cookies.json'
    csv_file = 'tweets.csv'
    image_to_post = 'image.jpg'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = None

        if os.path.exists(cookies_file):
            print(f"Loading cookies from {cookies_file}")
            context = await browser.new_context(storage_state=cookies_file)
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
                print(f"Saving authentication state to {cookies_file}...")
                await context.storage_state(path=cookies_file)
                print("Cookies saved successfully.")
            else:
                print("Successfully logged in using existing cookies.")

            # --- Process tweets from CSV ---
            if not os.path.exists(csv_file):
                print(f"Error: CSV file '{csv_file}' not found. Please create it.")
                return

            with open(csv_file, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    tweet_text = row.get('tweet_text', '')
                    if not tweet_text:
                        print(f"Skipping row {i+1} due to empty tweet_text.")
                        continue

                    print(f"\n--- Posting tweet {i+1} ---")
                    await post_tweet(page, tweet_text, image_path=image_to_post)

        except Exception as e:
            print(f"An error occurred: {e}")
            await page.screenshot(path='error_screenshot.png')
            print("A screenshot has been saved as 'error_screenshot.png' for debugging.")

        finally:
            print("\nAll tweets posted. Closing browser.")
            await browser.close()

if __name__ == '__main__':
    # Ensure a dummy image exists if the user hasn't provided one.
    image_to_post = 'image.jpg'
    if not os.path.exists(image_to_post):
        print(f"Warning: Test image '{image_to_post}' not found.")
        print("A dummy file will be created. Please replace it with a real image.")
        with open(image_to_post, 'w') as f:
            f.write("This is a dummy file for testing.")

    asyncio.run(main())
