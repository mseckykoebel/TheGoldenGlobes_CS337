# required
import nltk

# not required
import json
import sys
import random
import time
import csv

# helper file
import helpers
from getTweetText import getTweets 

def winnerFromNominees():

    # tweetText
    # tweets
    tweetFile = sys.argv[1]
    numberOfTweets = sys.argv[2]

    tweetText = getTweets(tweetFile, numberOfTweets)

    # for testing
    print(tweetText)

    return