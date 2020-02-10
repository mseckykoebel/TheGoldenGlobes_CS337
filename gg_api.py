#!/usr/bin/env python
# required and not required
from helpers import getTeamMembers
from helpers import getIMDbData
from getTweetText import getTweets
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from collections import Counter
import nltk
import numpy
import json
import re
import statistics
import sys
import time
import gzip
import ssl

# opens IMDb url
import urllib.request
from collections import Counter

# compare hashable sentences
from difflib import SequenceMatcher

# spacy, spacy tokenizer (for best and worst dressed)
import spacy
from spacy.tokenizer import Tokenizer
spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm")
tokenizer = Tokenizer(nlp.vocab)

# helper functions


"""Version 0.35"""

# pre-defined award names
OFFICIAL_AWARDS_1315 = [
    "cecil b. demille award",
    "best motion picture - drama",
    "best performance by an actress in a motion picture - drama",
    "best performance by an actor in a motion picture - drama",
    "best motion picture - comedy or musical",
    "best performance by an actress in a motion picture - comedy or musical",
    "best performance by an actor in a motion picture - comedy or musical",
    "best animated feature film",
    "best foreign language film",
    "best performance by an actress in a supporting role in a motion picture",
    "best performance by an actor in a supporting role in a motion picture",
    "best director - motion picture",
    "best screenplay - motion picture",
    "best original score - motion picture",
    "best original song - motion picture",
    "best television series - drama",
    "best performance by an actress in a television series - drama",
    "best performance by an actor in a television series - drama",
    "best television series - comedy or musical",
    "best performance by an actress in a television series - comedy or musical",
    "best performance by an actor in a television series - comedy or musical",
    "best mini-series or motion picture made for television",
    "best performance by an actress in a mini-series or motion picture made for television",
    "best performance by an actor in a mini-series or motion picture made for television",
    "best performance by an actress in a supporting role in a series, mini-series or motion picture made for television",
    "best performance by an actor in a supporting role in a series, mini-series or motion picture made for television",
]
OFFICIAL_AWARDS_1819 = [
    "best motion picture - drama",
    "best motion picture - musical or comedy",
    "best performance by an actress in a motion picture - drama",
    "best performance by an actor in a motion picture - drama",
    "best performance by an actress in a motion picture - musical or comedy",
    "best performance by an actor in a motion picture - musical or comedy",
    "best performance by an actress in a supporting role in any motion picture",
    "best performance by an actor in a supporting role in any motion picture",
    "best director - motion picture",
    "best screenplay - motion picture",
    "best motion picture - animated",
    "best motion picture - foreign language",
    "best original score - motion picture",
    "best original song - motion picture",
    "best television series - drama",
    "best television series - musical or comedy",
    "best television limited series or motion picture made for television",
    "best performance by an actress in a limited series or a motion picture made for television",
    "best performance by an actor in a limited series or a motion picture made for television",
    "best performance by an actress in a television series - drama",
    "best performance by an actor in a television series - drama",
    "best performance by an actress in a television series - musical or comedy",
    "best performance by an actor in a television series - musical or comedy",
    "best performance by an actress in a supporting role in a series, limited series or motion picture made for television",
    "best performance by an actor in a supporting role in a series, limited series or motion picture made for television",
    "cecil b. demille award",
]
# choosing between the years
#OFFICIAL_AWARDS_FOR_FUNCTION

global stopword

# lists for the return funcion
HOSTS = []
AWARDS = {}
NOMINEES = {}
WINNERS = {}
PRESENTERS = {}
# tweet dictionary
TWEETS = {}

# Defining program constants
AWARD_TOKEN_SET = set()
# possible keywords for the ceremoney itself
AWARD_KEYWORDS = [
    "#goldenglobes",
    "goldenglobes2013",
    "goldenglobes2015",
    "golden globes",
    "golden",
    "globes",
    "gg2013",
    "gg2015",
    "gg2020",
]

# all of the names in the IMDb database are going to go here
nameDictionary = {}

# all the stopwords can be added here
global function_stopwords
function_stopwords = stopwords.words("english")
function_stopwords.extend(
    [
        "golden",
        "globes",
        "hosted",
        "http",
        "co",
        "GoldenGlobes",
        "backstage",
        "presenters",
        "best",
        "actress",
        "actor",
        "tv",
        "movie",
        "miniseries",
        "presenting",
        "motion",
        "picture",
        "supporting",
        "goldenglobe",
        "st",
        "award",
        "cecil",
        "b",
        "demille",
        "looked",
        "whats",
        "happening",
        "original",
        "score",
        "screenplay",
        "RT",
        "hosting",
        "goldenglobes",
    ]
)


def pre_ceremony():
    """This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns."""

    """Creates a tsv file of the names of all of the actors on the
    IMDb database, their birth and death year, primary profession, and"""

    global nameDictionary

    print("Beginning the pre-ceremony process...")
    # TIMER START
    timer = time.time()

    f = getIMDbData()

    print("Processing data to nameDictionary (data.tsv can be opened with excel)")
    print("\n")

    f = gzip.open("nameBasics.tsv.gz")
    # read the file as strings
    dataContent = str(f.read())
    # split the content where there is a new line
    dataSeparators = dataContent.split("\\n")
    # split the lines with tab
    # all of the data will be in the array
    allData = []
    for line in dataSeparators:
        allData.append(line.split("\\t"))
    # define the dictionary of names
    global nameDictionary
    # only take names from a certian time (assuming this is not tested earlier)
    for year in range(2010, 2020):
        nameDictionary[str(year)] = []

    # iterate through all lines
    for name in allData[1 : len(allData) - 1]:
        # get the name, birth date, and death date
        name_name = name[1]
        name_birth = name[2]
        name_death = name[3]

        # if we're missing data, continue
        if name_birth == "\\\\N":
            continue

        # check if they're still alive
        if name_death == "\\\\N":
            years_active = range(int(name_birth), 2020)
        else:
            years_active = range(int(name_birth), int(name_death) + 1)

        # check that they weren't born before they died
        if years_active == range(1, 1):
            continue

        # check edge cases
        if years_active[0] < 2010 and years_active[-1] < 2010:
            continue
        if years_active[-1] > 2019:
            continue
        if years_active[0] < 2010:
            years_active = range(2010, years_active[-1] + 1)
        # add the years active to the array
        for year in years_active:
            nameDictionary[str(year)].append(name_name)

    print("Pre-ceremony processing complete.")

    print("\n")

    # TIMER END
    print("Total runtime: %s seconds" % str(time.time() - timer))

    print("\n")

    # print(nameDictionary)

    return


def get_hosts(year):
    """Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns."""

    print("Now getting hosts in year " + year + "\n")

    # ------ get json file
    f = "gg" + str(year) + ".json"

    # ------ get all tweets in a list
    tweets = getTweets(f, " ")

    # ------ use re.findall to get a list of tweets that may have host names
    match_list = []
    for tweet in tweets:
        matches = re.findall(r"[hH]osted", tweet)
        if matches != []:
            match_list.extend([tweet])

    # ------ get a list of all the tokens
    all_tokens = []
    tokenizer = RegexpTokenizer(r"\w+")
    for line in match_list:
        tokens = tokenizer.tokenize(line)
        all_tokens.extend(tokens)

    # ------ remove stopwords from token list
    for t in all_tokens:
        if t.lower() in function_stopwords:
            all_tokens.remove(t)

    # ------ find most common pairs (likely the host names)
    pairs = list(map(tuple, zip(all_tokens, all_tokens[1:])))
    common_pairs = Counter(pairs).most_common(2)

    # ------ determine whether there are one or two hosts and return
    if common_pairs[0][1] - common_pairs[1][1] < 15:
        hosts = [" ".join(common_pairs[0][0])]
        hosts.append(" ".join(common_pairs[1][0]))
    else:
        hosts = [" ".join(common_pairs[0][0])]

    # print(hosts)
    global HOSTS
    HOSTS = hosts
    print("Hosts gathered! \n")
    return hosts


def get_awards(year):
    """Awards is a list of strings. Do NOT change the name
    of this function or what it returns."""
    # Your code here
    # 1. list of words related to awards/helper words (maybe too many words? taken from list of awards above)
    award_word_dict = [
        "actor",
        "actress",
        "animated",
        "award",
        "best",
        "cecil",
        "comedy",
        "demille",
        "director",
        "drama",
        "feature",
        "film",
        "foreign",
        "language",
        "made",
        "mini",
        "series",
        "motion",
        "musical",
        "original",
        "performance",
        "picture",
        "role",
        "score",
        "screenplay",
        "series",
        "song",
        "supporting",
        "television",
    ]
    basic_word_dict = ["a", "an", "for", "in", "by", "or", "-", ":", ","]
    # 2. get tweets and tokenize them
    f = "gg" + str(year) + ".json"
    tweets = [nltk.word_tokenize(tweet) for tweet in getTweets(f, ' ')]
    # 3. look for award names in tweets
    awards = []  # return array
    award_tweets = []
    for tweet in tweets:
        if len(set(award_word_dict).intersection(tweet)) > 3:
            award_tweets.append(tweet)
    # 4. look for award words in award tweets
    for tweet in award_tweets:
        if "best" not in tweet and "cecil" not in tweet:
            continue
        award_name_builder = []
        begin = tweet.index("best") if "best" in tweet else tweet.index("cecil")
        is_in_award_dict = True
        for i in range(begin, len(tweet)):
            if tweet[i] not in award_word_dict and tweet[i] not in basic_word_dict:
                is_in_award_dict = False
            if (
                tweet[i] in award_word_dict
                or tweet[i] in basic_word_dict
                and is_in_award_dict
            ):
                award_name_builder.append(tweet[i])
        while award_name_builder[-1] in basic_word_dict:
            award_name_builder.pop()
        award_string = " ".join(award_name_builder)
        if award_string not in awards and len(award_name_builder) > 3:
            awards.append(award_string)

    global AWARDS
    AWARDS = awards
    return awards


def get_nominees(year):
    """Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns."""
    nominees = {}
    # your code here
    global NOMINEES
    NOMINEES = nominees
    return nominees


def get_winner(year):
    """Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns."""
    winners = {}
    # Your code here
    global WINNERS
    WINNERS = winners
    return winners


def get_presenters(year):
    """Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns."""
    presenters = {}
    # Your code here
    global PRESENTERS
    PRESENTERS = presenters
    return presenters


def main():
    """This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns."""
    return


# function that returns human-readbale format for data, as well as json format
def output(
    type,
    hosts=[],
    awards={},
    nominees={},
    winners={},
    presenters={},
):
    # if it is human readable or json, do something else
    if (type == "human") or (type == "Human"):
        output = " "
        # hosts if there is more than one
        output += "Host" + ("s: " if len(hosts) > 1 else ": ")
        # go through and grab the hosts
        for host in hosts:
            output += host + ", "
        # output
        output = output[:-2] + "\n\n"
        # AWARDS TODO
        return output
    elif (type == "json") or (type == "JSON") or (type == "Json"):
        output = {}
        # return the right output
        return output
    else:
        return None


# function that runs all of the code and returns in in a readable way
def runAllFunctions(year):
    # run all of the functions
    get_hosts(year)
    # get_awards(year)
    # get_nominees(year)
    # get_presenters(year)
    # get_winner(year)
    # bestDressed = best_dressed(year)
    # worstDressed = worst_dressed(year)
    # output
    print("Generating output and output file...\n")
    humanOutput = output(
        "human",
        HOSTS,
        AWARDS,
        NOMINEES,
        WINNERS,
        PRESENTERS,
    )
    # add this when it is done!!!!! :
    #{"Best Dressed": bestDressed, "Worst Dressed": worstDressed}
    jsonOutput = output("json", HOSTS)
    """jsonOutput = output("json", HOSTS, AWARDS, NOMINEES, WINNERS, PRESENTERS)"""
    # create the json file
    with open("data" + str(year) + ".json", "w") as f:
        json.dump(jsonOutput, f)
    # print to the console
    print(humanOutput)
    return


### BONUS FUNCTIONS ###


"""def best_dressed(year):
    # define an array that will hold the right data
    global OFFICIAL_AWARDS_FOR_FUNCTION
    # get the 2013, 2015, 2018, or 2019 data
    if (year == "2013") or (year == "2015"):
        OFFICIAL_AWARDS_FOR_FUNCTION = OFFICIAL_AWARDS_1315
        print("Using OFFICIAL_AWARDS_1315 \n")
    elif (year == "2018") or (year == "2019"):
        OFFICIAL_AWARDS_FOR_FUNCTION = OFFICIAL_AWARDS_1819
        print("Using OFFICIAL_AWARDS_1819 \n")
    else:
        ValueError("Please use data from 2013, 2015, 2018, or 2019!")
    # tweets array
    global TWEETS
    stopwords = []
    """"""stopwords = [
        "#goldenglobes",
        "goldenglobes2013",
        "goldenglobes2015",
        "goldenglobes2018",
        "goldenglobes2019",
        "golden globes",
        "golden",
        "globes",
        "gg2013",
        "gg2015",
        "gg2018",
        "gg2019",
    ] """"""
    bestDressedKeywords = [
        "alluring",
        "appealing",
        "amazing",
        "beautiful",
        "dazzling",
        "delicate",
        "elegant",
        "exquisite",
        "gorgeous",
        "stunning",
        "wonderful",
        "best dressed",
        "best dress",
        "best looking",
        "magnificent",
        "lovely dress",
        "dapper",
        "graceful",
        "fantastic suit",
        "handsome outfit",
        "great outfit",
        "best dressed",
    ]
    # iterate through all of the tweets and if one of the key words matches, add it to the matching tweets array
    for tweet in TWEETS:
        # add to the matching tweet array of any of the words are the same
        if any(word in tweet for word in bestDressedKeywords):
            matchingTweets = []
            matchingTweets.append(tweet)

    bestDressedNames = commonWords(matchingTweets, "PERSON", year)
    # new dictionary for work with
    newDictionary = {}
    for person in bestDressedNames:
        # if we use one of the official tweets, we need to discard it
        if person in stopwords:
            continue
        # return if the value exists in the keywords list, and none if it does not
        k = valueExistsInKeyWords(newDictionary, person)
        # depending on if the person is in the dictionary
        if k is None:
            newDictionary[person] = bestDressedNames[person]
        else:
            # they are in so add to the dictionary
            newDictionary[k] = newDictionary[k] + bestDressedNames[person]
    # counts the number of elements in the string
    counter = Counter(bestDressedNames)
    # if we have more than one person in the array, make an array of the result
    if (len(counter.most_common(1)) > 0):
        # store the result
        result = []
        result = [person[0] for person in counter.most_common(5) if person]
    else:
        ValueError("I suppose nobody was dressed that well :/")
    # return the list of the best dressed
    return result


def worst_dressed(year):
    # define an array that will hold the right data
    global OFFICIAL_AWARDS_FOR_FUNCTION
    # get the 2013, 2015, 2018, or 2019 data
    if (year == "2013") or (year == "2015"):
        OFFICIAL_AWARDS_FOR_FUNCTION = OFFICIAL_AWARDS_1315
        print("Using OFFICIAL_AWARDS_1315 \n")
    elif (year == "2018") or (year == "2019"):
        OFFICIAL_AWARDS_FOR_FUNCTION = OFFICIAL_AWARDS_1819
        print("Using OFFICIAL_AWARDS_1819 \n")
    else:
        ValueError("Please use data from 2013, 2015, 2018, or 2019!")
    # resulting array and tweets of interest
    result = []
    
    # scan through all of the tweets
    return result"""

def commonWords(tweets, type, year):
    words = {}
    return words

def valueExistsInKeyWords(keysList, val):
    for key in keysList:
        return key 
    else:
        # there was no key in the key list
        return None


# run these before main
getTeamMembers()
pre_ceremony()

if __name__ == "__main__":
    # elapsedSeconds = seconds since 0
    elapsedSeconds = time.time()
    # run the function
    main()
    # run the helper functions with the given year
    runAllFunctions(sys.argv[1])
    # print the amount of time the program took
    print(time.time() - elapsedSeconds)
