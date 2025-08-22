import asyncio
import json
import os
from playwright.async_api import async_playwright

async def main():
    """
    This function launches a browser, loads cookies, navigates to Twitter,
    and posts a tweet.
    """
    cookies_file = 'twitter_cookies.json'
    if not os.path.exists(cookies_file):
        print(f"Error: {cookies_file} not found.")
        print("Please create this file and add your Twitter cookies to it.")
        print("You can use a browser extension like 'Cookie-Editor' to export your cookies.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=True for background execution
        context = await browser.new_context(storage_state=cookies_file)
        page = await context.new_page()

        try:
            print("Navigating to Twitter...")
            await page.goto('https://twitter.com/home', timeout=60000)

            print("Waiting for the tweet textarea...")
            textarea_selector = "//div[@contenteditable='true' and contains(@role, 'textbox')]"
            await page.wait_for_selector(textarea_selector, timeout=60000)

            print("Typing the tweet...")
            tweet_text = 'Welcome to automation life'
            await page.locator(textarea_selector).fill(tweet_text)

            print("Waiting for the post button...")
            post_button_selector = "button[data-testid='tweetButton']"
            await page.wait_for_selector(post_button_selector, timeout=60000)

            # Ensure the button is enabled before clicking
            await page.wait_for_function(f"document.querySelector('{post_button_selector}').disabled === false")

            print("Clicking the post button...")
            await page.locator(post_button_selector).click()

            print("Tweet posted successfully!")
            await page.wait_for_timeout(5000)  # Wait 5 seconds to see the result

        except Exception as e:
            print(f"An error occurred: {e}")
            await page.screenshot(path='error_screenshot.png')
            print("A screenshot has been saved as 'error_screenshot.png' for debugging.")

        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
