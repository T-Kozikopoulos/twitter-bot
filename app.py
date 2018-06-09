# Make sure you use the name of your credentials file and it is in the same directory as this file.
import credentials
# For connecting to and handling everything related to the Twitter API.
from tweepy import API, Cursor, Stream, OAuthHandler
from tweepy.streaming import StreamListener
# For sentiment analysis.
from textblob import TextBlob


# Twitter authenticator.
def authenticate_twitter_app():
    auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
    return auth


# Find and analyze tweets by going through a hashtag.
def search_for_tweets(hashtag):
    auth = authenticate_twitter_app()
    api = API(auth)
    tweets = api.search(hashtag)
    for tweet in tweets:
        # Print out the contents of each tweet.
        print(tweet.text)
        # Analyze each tweet based on polarity(negative/neutral/positive) and objectivity(how biased it is).
        analysis = TextBlob(tweet.text)
        print(analysis.sentiment)


# Twitter user's profile you want to search.
class TwitterClient:

    def __init__(self, twitter_user=None):
        self.auth = authenticate_twitter_app()
        self.client = API(self.auth)
        self.twitter_user = twitter_user

    def get_timeline_tweets(self, num_tweets):
        tweets = []
        # Specifying how many tweets to pull from a timeline.
        for tweet in Cursor(self.client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)

        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)

        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        timeline_tweets = []
        for tweet in Cursor(self.client.home_timeline, id=self.twitter_user).items(num_tweets):
            timeline_tweets.append(tweet)

        return timeline_tweets


# Live streaming and processing tweets.
class TwitterStreamer:

    # Authenticate and connect to Twitter API.
    def stream_tweets(self, saved_tweets_filename, hashtag_list):
        # Save tweets you process to a file.
        listener = TwitterListener(saved_tweets_filename)

        auth = authenticate_twitter_app()

        stream = Stream(auth, listener)
        # Specify the hashtags you're interested in.
        stream.filter(track=hashtag_list)


# Basic listener for printing out tweets.
class TwitterListener(StreamListener):

    def __init__(self, saved_tweets_filename):
        self.saved_tweets_filename = saved_tweets_filename

    # Print out and save to a file the results of your search.
    def on_data(self, tweet_data):

        try:
            print(tweet_data)
            with open(self.saved_tweets_filename, 'a') as f:
                f.write(tweet_data)

            return True

        except BaseException as e:
            print(str(e))

        return True

    def on_error(self, status):
        # When getting blocked from Twitter for reaching the rate limit, stop the script.
        if status == 420:
            return False
        print(status)


if __name__ == '__main__':

    # Pick hashtags you're interested in, as many as you want.
    hashtag_list = ['youtube']
    # Choose the name/type of the file you want to save the tweets, and all their metadata, in.
    saved_tweets_filename = 'tweets.json'

    # Specify the Twitter handle of the user's timeline you're interested in.
    client = TwitterClient('warrenellis')
    print(client.get_timeline_tweets(5))

    # Live stream tweets and save them in a file as you go.
    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(saved_tweets_filename, hashtag_list)

    # This is the equivalent of "Twitter Search'.
    search_for_tweets('python')
    
