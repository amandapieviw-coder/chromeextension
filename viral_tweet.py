import tweepy

def get_api_keys():
    """Prompts the user to enter their Twitter API keys."""
    print("You'll need to get Twitter API keys to use this script.")
    print("You can get them by applying for a developer account at https://developer.twitter.com/")
    api_key = input("Enter your API Key: ")
    api_secret_key = input("Enter your API Secret Key: ")
    access_token = input("Enter your Access Token: ")
    access_token_secret = input("Enter your Access Token Secret: ")
    return api_key, api_secret_key, access_token, access_token_secret

def get_trends(api):
    """Fetches the top 10 worldwide trending topics."""
    try:
        trends = api.get_place_trends(id=1)[0]['trends']
        return trends[:10]
    except Exception as e:
        print(f"Error fetching trends: {e}")
        return None

def get_tweet():
    """Asks the user for the text of their tweet."""
    return input("Enter the text of your tweet: ")

def display_tips():
    """Displays tips for making a tweet more engaging."""
    print("\n--- Tips for a more engaging tweet: ---")
    print("- Consider adding an image, GIF, or video.")
    print("- Ask a question to encourage replies.")
    print("- Use a poll to get opinions.")
    print("- Keep it concise and easy to read.")
    print("----------------------------------------\n")

def main():
    """Main function to run the script."""
    api_key, api_secret_key, access_token, access_token_secret = get_api_keys()

    try:
        auth = tweepy.OAuthHandler(api_key, api_secret_key)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    trends = get_trends(api)

    if trends:
        print("\n--- Top 10 Worldwide Trends: ---")
        for i, trend in enumerate(trends):
            print(f"{i+1}. {trend['name']}")
        print("---------------------------------\n")

    tweet = get_tweet()

    display_tips()

    print(f"Your tweet: {tweet}")
    if trends:
        print("Consider adding some of the trending hashtags to your tweet to increase its visibility.")


if __name__ == "__main__":
    main()
