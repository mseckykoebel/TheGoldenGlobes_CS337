#!/usr/bin/env python
# required and not required
from helpers import getTeamMembers
from helpers import getIMDbData
from getTweetText import getTweets
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from collections import Counter
from difflib import SequenceMatcher
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

# spacy and the spacy tokenizer
import spacy
from spacy.tokenizer import Tokenizer

spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm")

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
# OFFICIAL_AWARDS_FOR_FUNCTION


global stopword

# lists for the return funcion
HOSTS = []
AWARDS = {}
NOMINEES = {}
WINNERS = {}
PRESENTERS = {}

# Defining program constants
AWARD_TOKEN_SET = set()
# possible keywords for the ceremony itself
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
# tweet dictionary
TWEETS = {}

# all of the names in the IMDb database are going to go here
nameDictionary = {}
award_word_dict = ['actor', 'actress', 'animated', 'award', 'best',  'cecil', 'comedy', 'demille', 'director', 'drama', 'feature', 'film', 'foreign',
                   'language', 'made', 'mini', 'series', 'motion', 'musical',  'original', 'performance', 'picture', 'role', 'score', 'screenplay', 'series', 'song', 'supporting', 'television']


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

    #f = gzip.open("nameBasics.tsv.gz")
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
    for name in allData[1: len(allData) - 1]:
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
    tweets = [nltk.word_tokenize(tweet) for tweet in getTweets(f, 100000)]
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
        begin = tweet.index(
            "best") if "best" in tweet else tweet.index("cecil")
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
    awards = dedup(awards)
    global AWARDS
    AWARDS = awards
    return awards


def dedup(awards):
    duplicates = []
    for i in range(len(awards)-1):
        for j in range(i, len(awards)):
            a = awards[i]
            b = awards[j]
            if a != b:
                similarity = SequenceMatcher(None, a, b).ratio()
                if similarity > .85:
                    if not ('actor' in a and 'actress' in b or 'actor' in a and 'actress' in b):
                        if not ('actor' in a and 'actor' not in b or 'actress' in a and 'actress' not in b):
                            duplicates.append(b)
    duplicates = set(duplicates)
    for x in duplicates:
        if x in awards:
            awards.remove(x)
    return awards


def get_nominees(year):
    """Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns."""
    # Your code here
    global award_word_dict

    nominees = {k: [] for k in OFFICIAL_AWARDS_1315}
    awards_tokenized = [nltk.word_tokenize(
        award) for award in OFFICIAL_AWARDS_1315]
    key_words = ['nominates', 'nominees', 'nominate', 'nominated', 'nominee', 'award',
                 'nom', 'noms', 'win', 'won', 'wins', 'winner']
    basic_word_dict = ['a', 'an', 'for', 'in', 'by', 'or', '-', ':', ',']

    f = 'gg'+str(year)+'.json'
    tweets = [nltk.word_tokenize(tweet.lower()) for tweet in getTweets(f, 100000)]

    actor_names = [name.lower() for name in nameDictionary[str(int(year)-1)]]

    award_tweets = []
    for tweet in tweets:
        if len(set(award_word_dict).intersection(tweet)) > 2:
            award_tweets.append(tweet)

    for tweet in award_tweets:
        # There is nominee keyword present
        if len((set(key_words) & set(tweet))) > 0:
            # full_tweet = tweet[0]
            candidate = ''
            award = ''
            for i in range(1, len(tweet)):
                # full_tweet = full_tweet + ' ' + tweet[i]
                c = tweet[i - 1] + ' ' + tweet[i]
                if c in actor_names:
                    candidate = c
                    break

            if candidate:
                for a in awards_tokenized:
                    if len(set(a).intersection(tweet)) > len(set(a))/2:
                        award = " ".join(a)
                        break

            if candidate and award:
                if candidate not in nominees[award]:
                    nominees[award].append(candidate)
    print(nominees)
    return nominees


def get_winner(year):
    """Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns."""
    # Your code here
    return winners


def get_presenters(year):
    """Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns."""
    # Your code here
    presenters = {}
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
    bestAndWorstDressed=[],
):
    # if it is human readable or json, do something else
    if (type == "human") or (type == "Human"):
        output = ""
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
    get_awards(year)
    get_nominees(year)
    get_presenters(year)
    get_winner(year)
    bestDressed = best_dressed(year)
    worstDressed = worst_dressed(year)
    # output
    humanOutput = output(
        "human",
        HOSTS,
        AWARDS,
        NOMINEES,
        WINNERS,
        PRESENTERS,
        {"Best Dressed": bestDressed, "Worst Dressed": worstDressed},
    )
    jsonOutput = output("json", HOSTS, AWARDS, NOMINEES, WINNERS, PRESENTERS)
    # create the json file
    with open("data" + str(year) + ".json", "w") as f:
        json.dump(jsonOutput, f)
    # print to the console
    print(humanOutput)
    return


### BONUS FUNCTIONS ###


def best_dressed(year):
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

    result = []
    # iterate through all of the tweets and if one of the key words matches, add it to the matching tweets array
    # for tweet in TWEETS
    # matchingTweets = []
    # matchingTweets.append(tweet)

    # listOfBestDressed = .....
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
    # TODO
    result = []
    return result


# run these before main
getTeamMembers()
pre_ceremony()
get_nominees('2013')
# get_awards('2013')

if __name__ == "__main__":
    # elapsedSeconds = seconds since 0
    elapsedSeconds = time.time()
    # run the function
    main()
    # run the helper functions with the given year
    runAllFunctions(sys.argv[1])
    # print the amount of time the program took
    print(time.time() - elapsedSeconds)
