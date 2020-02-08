import json
import sys
import random

# function that can take in json tweet file, and optional
# second argument for number of tweets wanted
def getTweets(tweetFile, numOfTweets):

    # open the tweet file
    with open(tweetFile) as read_file:
        tweets = json.load(read_file)

    # get the second argument
    if numOfTweets == ' ':
        tweetText = []
        for i in tweets:
            tweetText.append(i["text"])
    else:
        numberOfTweets = int(numOfTweets)

        # take a random subset of the number of tweets entered
        tweets = random.sample(tweets, numberOfTweets)

        # take only text
        tweetText = []
        for i in tweets:
            tweetText.append(i["text"])

    return tweetText
