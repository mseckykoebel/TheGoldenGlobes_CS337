import json
import sys
import random
from helpers import extractTextFromFile

# function that can take in json tweet file, and optional
# second argument for number of tweets wanted

def getTweets():

    # if more arguments are entered, there as an error
    if len(sys.argv) > 3:
        print(
            """Wrong number of arguments. Please include only the .json
            data file, or the data file, and the total number of tweets
            you want to test with 
            (recommended to make the computation much faster)!"""
        )
        sys.exit(2)

    # open the tweet file
    with open(sys.argv[1]) as read_file:
        tweets = json.load(read_file)

    # get the second argument
    numberOfTweets = int(sys.argv[2])

    # take a random subset of the number of tweets entered
    tweets = random.sample(tweets, numberOfTweets)

    # take only text
    tweetText = []
    for i in tweets:
        tweetText.append(i['text'])

    return tweetText