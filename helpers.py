# required and not required
import nltk
import json
import re
import sys
import time
import gzip
import ssl
import os
import random
# opens IMDb url
import urllib.request
from collections import Counter
# compare hashable sentences
from difflib import SequenceMatcher

# get the name of the project members
class TeamMember:

    def __init__(self, name, netID):
        self.name = name
        self.netID = netID

    def _get_name(self):
        return self.name

member1 = TeamMember("Mason Secky-Koebel", "msf9197")
member2 = TeamMember("Tyler Rodgers", "tcr7461")
member3 = TeamMember("Ryan Jeon", "yjj3249")
member4 = TeamMember("Meera Ramakrishnan", "")

def getTeamMembers():
    print('Team members: \n')
    print(member1._get_name() + ", " + member2._get_name() + ", " + member3._get_name() + ", " + member4._get_name())
    print("\n")

def extractText(json_obj):
    """ 
	Helper function to extract comments from JSON obj.
	Arguments : JSON Obj of tweets
	Output	  : List of comments strings
	"""
    comment_list = []
    for comment in json_obj:
        text = comment if type(comment) is str else comment["text"]
        comment_list.append(text)

    return comment_list

def extractTextFromFile(path):
    """ 
	Helper function to extract comments from JSON tweets.
	Arguments : JSON file directory (Tweets)
	Output	  : List of comments strings
	"""

    with open(path) as read_file:
        data = json.load(read_file)

    comments = extractText(data)
    print(comments)
    return comments

# function that downloads the IMBd database name data
def getIMDbData():
    # this can be opened with excel, or VSCode
    ssl._create_default_https_context = ssl._create_unverified_context
    # download names from IMDB about (https://datasets.imdbws.com/)
    print("Downloading name.basics.tsv.gz from https://datasets.imdbws.com/ \n")
    # download the file and store as nameBasics

    if os.path.exists('./nameBasics.tsv.gz'):
        print("nameBasics.tsv.gz already exists in the directory. Remove the file if you wish to update! \n")
    else:
        urllib.request.urlretrieve('https://datasets.imdbws.com/name.basics.tsv.gz', 'nameBasics.tsv.gz')
    print("Download complete! \n")

    print("Downloading title.basics.tsv.gz from https://datasets.imdbws.com/")
    print("\n")
    # download the file and store as nameBasics

    if os.path.exists('./titleBasics.tsv.gz'):
        print("title.basics.tsv.gz already exists in the directory. Remove the file if you wish  to update!\n")
    else:
        urllib.request.urlretrieve('https://datasets.imdbws.com/title.basics.tsv.gz', 'titleBasics.tsv.gz')
    print("Download complete!")
    print("\n")




    # make and return the file
    file = gzip.open('nameBasics.tsv.gz')
    return file

# function that can take in json tweet file, and optional
# second argument for number of tweets wanted
def getTweets(tweetFile, numOfTweets):

    # open the tweet file
    with open(tweetFile) as read_file:
        tweets = json.load(read_file)

    # get the second argument
    numberOfTweets = int(numOfTweets)

    # take a random subset of the number of tweets entered
    tweets = random.sample(tweets, numberOfTweets)

    # take only text
    tweetText = []
    for i in tweets:
        tweetText.append(i["text"])

    return tweetText
