import tweepy
import json
import pandas as pd
import emoji
from math import ceil
import os
import sys
from datetime import datetime


def auth_tweepy(path="twitter_keys.json"):
    # import the API keys from the config file.
    with open(path) as f:
        creds = json.load(f)
        api_key = creds["key"]
        api_secret = creds["secret"]
        bearer_token = creds["bearer_token"]
        access_key = creds["access_token"]
        access_secret = creds["access_secret"]

    # Sign in
    auth = tweepy.auth.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_key, access_secret)

    return tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def fetch_tweets(
    queries,
    tweets_per_query,
    api,
    keys_to_keep=["created_at", "id", "full_text", "lang"],
    DRYRUN=False,
):
    print(f"This will run {str(len(queries))} queries")
    print(
        f"This search may take up to {ceil(len(queries)*tweets_per_query/100/180)*15} minutes"
    )

    if not DRYRUN:
        data_dir = os.path.join(os.getcwd(), "run_" + str(datetime.now()))
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        data = []

        for search_emoji in queries:
            last_id = -1
            tweets = []
            query = search_emoji + " -filter:retweets"
            print(f'Starting query "{query}"')
            while len(tweets) < tweets_per_query:
                count = tweets_per_query - len(tweets)
                try:
                    new_results = api.search(
                        q=query,
                        count=count,
                        lang="en",
                        max_id=str(last_id - 1),
                        tweet_mode="extended",
                    )
                    if not new_results:
                        break
                    tweets.extend(new_results)
                    last_id = new_results[-1].id
                except tweepy.TweepError as e:
                    # depending on TweepError.code, one may want to retry or wait
                    # to keep things simple, we will give up on an error
                    print(e)
                    break

            for tweet in tweets:
                filtered_tweet = {key: tweet._json[key] for key in keys_to_keep}
                data.append(filtered_tweet)

            if len(data) > 10000:
                print("Persisting current search results to disk")
                df = pd.DataFrame(data)
                df.to_csv(data_dir + "/" + str(datetime.now()) + ".csv", index=False)
                data = []

        if data:  # Clean up the rest of the data
            df = pd.DataFrame(data)
            df.to_csv(data_dir + "/" + str(datetime.now()) + ".csv", index=False)


if __name__ == "__main__":
    search_space = list(sys.argv[1])
    if "".join(search_space) == "ALL":
        search_space = [*emoji.UNICODE_EMOJI]

    tweets_per_query = int(sys.argv[2])
    api = auth_tweepy()
    df = fetch_tweets(search_space, tweets_per_query, api)