# required
import nltk
import spacy

# not required
import json
import sys
import random
import time
import csv
from imdb import IMDb

# helper file
from getTweetText import getTweets

# instance of imdb class
ia = IMDb()
# get the controlled number of tweets
tweets = getTweets(sys.argv[1], sys.argv[2])
