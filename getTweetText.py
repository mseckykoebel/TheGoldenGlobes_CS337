import json
import sys
import random

# function that can take in json tweet file, and optional
# second argument for number of tweets wanted

def getTweets(tweetFile, numberOfTweets):

    # if more arguments are entered, there as an error
    if len(sys.argv) > 2:
        print(
            """Wrong number of arguments. Please include only the .json
            data file, or the data file and the total number of tweets 
            (recommended to make the computation much faster)!"""
        )
        sys.exit(2)

    # get the tweets
    with open(tweetFile) as file:
        tweets = json.load(file)


    # make the number of tweets smaller if the argument was there
    if (numberOfTweets):
        tweets = random.sample(tweets, 10000)

    # get only the comments 
    comment_list = []

    # extract just the text
    for comment in tweets:
        text = comment if type(comment) is str else comment["text"]
        comment_list.append(text)

    # text only is appended and placed in an array 
    tweetText = []
    for i in tweets:
        tweetText.append(i['text'])

    # return the text
    return tweetText