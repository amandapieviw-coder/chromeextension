document.addEventListener('DOMContentLoaded', function() {
  const postThreadButton = document.getElementById('post-thread-button');
  const threadContent = document.getElementById('thread-content');

  postThreadButton.addEventListener('click', function() {
    const thread = threadContent.value;
    if (thread.trim() === '') {
      return;
    }

    const tweets = splitIntoTweets(thread);

    for (let i = 0; i < tweets.length; i++) {
      const tweet = tweets[i];
      const tweetUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(tweet)}`;
      chrome.tabs.create({ url: tweetUrl });
    }
  });

  function splitIntoTweets(text) {
    const maxLength = 280;
    const tweets = [];
    let currentTweet = '';

    const words = text.split(' ');

    for (const word of words) {
      if (currentTweet.length + word.length + 1 <= maxLength) {
        currentTweet += (currentTweet.length > 0 ? ' ' : '') + word;
      } else {
        tweets.push(currentTweet);
        currentTweet = word;
      }
    }

    if (currentTweet.length > 0) {
      tweets.push(currentTweet);
    }

    // Add numbering to the tweets if there are more than one
    if (tweets.length > 1) {
        for (let i = 0; i < tweets.length; i++) {
            const number = `(${i + 1}/${tweets.length})`;
            // Check if adding the number exceeds the maxLength
            if (tweets[i].length + number.length + 1 <= maxLength) {
                tweets[i] = `${tweets[i]} ${number}`;
            } else {
                // If it exceeds, we need to truncate the tweet and add the number
                const availableSpace = maxLength - (number.length + 1);
                tweets[i] = tweets[i].substring(0, availableSpace - 3) + '... ' + number;
            }
        }
    }

    return tweets;
  }
});
