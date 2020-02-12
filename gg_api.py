#!/usr/bin/env python
# required and not required
from helpers import getTeamMembers
from helpers import getIMDbData
from getTweetText import getTweets
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from collections import Counter
from difflib import SequenceMatcher
from bestAndWorstDressed import best_dressed
from bestAndWorstDressed import worst_dressed
import nltk
import numpy
import json
import re
import statistics
import sys
import time
import gzip
import ssl
import os

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
    "best actor in a comedy or musical TV series",
    "best motion picture screenplay",
    "best foreign language film",
    "best director",
    "best screenplay",
    "best original score",
    "best supporting actress",
    "best supporting actor",
    "best actress in a motion picture , comedy or musical",
    "best actor in a motion picture , comedy or musical",
    "best actor in a motion picture , drama",
    "best actor in a motion picture - drama",
    "best actress in a motion picture - drama",
    "best actress in a motion picture",
    "best actress in a TV series",
    "best performance",
    "best actor in a TV series",
    "best actress in a drama series",
    "best film in the comedy",
    "best performance by an actress in a supporting role in a motion picture",
    "best performance by an actor in a supporting role in a motion picture",
    "best director - motion picture",
    "best screenplay - motion picture",
    "best original score - motion picture",
    "best original song - motion picture",
    "best television series - drama",
    "best animated feature film",
    "best comedy or musical TV series",
    "best motion picture , comedy or musical",
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
OFFICIAL_AWARDS = None

global stopword

# lists for the return funcion
HOSTS = {}
AWARDS = {}
NOMINEES = {}
WINNERS = {}
PRESENTERS = {}
# tweet dictionary
ALLTWEETS = {}

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


# all of the names and movie titles are going to go here
nameDictionary = {}
movieDictionary = {}

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
        "animated",
        "film",
        "zap2it",
        "always",
        "good",
        "series",
        "goes",
        "presents",
        "drama",
        "needs",
        "jodie",
        "foster",
        "lay",
        "foreign",
        "bill",
        "clinton",
        "yahoo2movies",
        "yahoomovies",
        "introduced",
        "philstarnews",
        "lincolnmovie",
        "nomination",
        "msntv",
        "nominee",
        "lincoln",
        "maggie",
        "downtown",
        "abbey",
    ]
)


def init_files():
    global nameDictionary
    f = getIMDbData()

    print("Processing data to nameDictionary (data.tsv can be opened with excel)")
    print("\n")

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
    # only take names from a certain time (assuming this is not tested earlier)
    for year in range(2010, 2020):
        nameDictionary[str(year)] = []

    print("Processing data to movieDictionary (data.tsv can be opened with excel)")
    print("\n")

    f = gzip.open("titleBasics.tsv.gz")
    # read the file as strings
    dataContent_movie = str(f.read())
    # split the content where there is a new line
    dataSeparators_movie = dataContent_movie.split("\\n")
    # split the lines with tab
    # all of the data will be in the array
    allData_movie = []
    for line in dataSeparators_movie:
        allData_movie.append(line.split("\\t"))
    # define the dictionary of movies
    global movieDictionary

    # only take names from a certain time (assuming this is not tested earlier)
    for year in range(2010, 2020):
        movieDictionary[str(year)] = []

    for name in allData_movie[1 : len(allData_movie) - 1]:
        name_name = name[3]  # 1 before is english translation
        year = name[5]

        if name_name == "\\\\N" or year == "\\\\N":
            continue

        year = int(year)
        interested_years = range(2010, 2020)

        # add the years active to the array
        for year in interested_years:
            movieDictionary[str(year)].append(name_name)

    with open("movieDictionary.json", "w") as fp:
        json.dump(movieDictionary, fp)

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

    with open("nameDictionary.json", "w") as fp:
        json.dump(nameDictionary, fp)


def pre_ceremony():
    """This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns."""

    """Creates a tsv file of the names of all of the actors on the
    IMDb database, their birth and death year, primary profession, and"""

    global movieDictionary
    global nameDictionary

    print("Beginning the pre-ceremony process...")
    # TIMER START
    timer = time.time()

    if os.path.exists("./nameDictionary.json") and os.path.exists(
        "./movieDictionary.json"
    ):
        name_json = open("./nameDictionary.json")
        movie_json = open("./movieDictionary.json")
        nameDictionary = json.load(name_json)
        movieDictionary = json.load(movie_json)
    else:
        init_files()

    # TIMER END
    print("Total runtime: %s seconds" % str(time.time() - timer) + "\n")

    print("\n")

    return


def get_hosts(year):
    """Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns."""

    print("Getting list of hosts for year: " + year + "\n")

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
    global award_word_dict
    global ALL_TWEETS
    allTweets = ALL_TWEETS

    # 1. list of words related to awards/helper words
    # starting
    print("Getting list of awards for year: " + year + "\n")
    # 1. list of words related to awards/helper words (maybe too many words? taken from list of awards above)
    award_word_dict = [
        "award",
        "best",
        "performance",
        "picture",
        "tv",
        "television",
        "series",
        "honored",
        "honor",
        "actor",
        "actress",
        "song",
        "motion",
        "movie",
    ]
    basic_word_dict = ["a", "an", "for", "in", "by", "or", "-", ":", ","]
    invalid_dict = [
        "loser",
        "host",
        "hosts",
        "hosting",
        "opening",
        "accept",
        "acceptance",
        "speech",
        "nominee",
    ]
    # 2. get tweets and tokenize them
    f = "gg" + str(year) + ".json"
    tweets = []
    for tweet in allTweets:
        matches = re.findall(
            r"[bB][eE][sS][tT]|[cC][eE][cC][iI][lL]|[dD][eE][mM][iI][lL][lL][eE]", tweet
        )
        if matches:
            tweets.append(tweet)
    award_tweets_prelim = [nltk.word_tokenize(tweet) for tweet in tweets]
    # 3. look for award names in tweets
    awards = []  # return array
    award_tweets = []
    for tweet in award_tweets_prelim:
        if len(set(award_word_dict).intersection(tweet)) > 2:
            award_tweets.append(tweet)
    # 4. look for award words in award tweets
    for tweet in award_tweets:
        begin_str = ""
        if "best" in tweet:
            begin_str = "best"
        if "cecil" in tweet:
            begin_str = "cecil"
        if begin_str:
            award_name_builder = []
            begin = tweet.index(begin_str)
            is_in_award_dict = 0
            for i in range(begin, len(tweet)):
                if tweet[i] in invalid_dict:
                    continue
                if (
                    tweet[i][0].isupper()
                    and tweet[i] not in award_word_dict
                    and tweet[i] not in basic_word_dict
                ):
                    continue
                if tweet[i] not in award_word_dict and tweet[i] not in basic_word_dict:
                    is_in_award_dict += 1
                if (
                    tweet[i] in award_word_dict
                    or tweet[i] in basic_word_dict
                    or is_in_award_dict < 2
                ):
                    award_name_builder.append(tweet[i])
            while award_name_builder[-1] in basic_word_dict:
                award_name_builder.pop()
            award_string = " ".join(award_name_builder)
            if award_string not in awards and len(award_name_builder) > 3:
                awards.append(award_string)
    awards = clean(awards)
    global AWARDS
    AWARDS = awards
    print(awards)
    print("Awards gathered! \n")
    return awards

def clean(awards):
    duplicates = []
    for i in range(len(awards) - 1):
        for j in range(i, len(awards)):
            a = awards[i]
            b = awards[j]
            if a != b:
                similarity = SequenceMatcher(None, a, b).ratio()
                if similarity > 0.7:
                    if not (
                        "actor" in a
                        and "actress" in b
                        or "actor" in a
                        and "actress" in b
                    ):
                        if not (
                            "actor" in a
                            and "actor" not in b
                            or "actress" in a
                            and "actress" not in b
                        ):
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
    # print
    print("Getting the nominees for year: " + year + "\n")
    nominees = {k: [] for k in OFFICIAL_AWARDS_1315}
    awards_tokenized = [nltk.word_tokenize(award) for award in OFFICIAL_AWARDS_1315]
    key_words = [
        "nominates",
        "nominees",
        "nominate",
        "nominated",
        "nominee",
        "award",
        "nom",
        "noms",
        "win",
        "won",
        "wins",
        "winner",
    ]
    basic_word_dict = ["a", "an", "for", "in", "by", "or", "-", ":", ","]

    f = "gg" + str(year) + ".json"
    tweets = [nltk.word_tokenize(tweet.lower()) for tweet in getTweets(f, 100000)]

    actor_names = [name.lower() for name in nameDictionary[str(int(year) - 1)]]

    award_tweets = []
    for tweet in tweets:
        if len(set(award_word_dict).intersection(tweet)) > 2:
            award_tweets.append(tweet)

    for tweet in award_tweets:
        # There is nominee keyword present
        if len((set(key_words) & set(tweet))) > 0:
            # full_tweet = tweet[0]
            candidate = ""
            award = ""
            for i in range(1, len(tweet)):
                # full_tweet = full_tweet + ' ' + tweet[i]
                c = tweet[i - 1] + " " + tweet[i]
                if c in actor_names:
                    candidate = c
                    break

            if candidate:
                for a in awards_tokenized:
                    if len(set(a).intersection(tweet)) > len(set(a)) / 2:
                        award = " ".join(a)
                        break

            if candidate and award:
                if candidate not in nominees[award]:
                    nominees[award].append(candidate)
    # print(nominees)
    global NOMINEES
    NOMINEES = nominees
    print("Nominees Gathered! \n")
    return nominees


def get_winner(year):
    """Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns."""
    # Your code here
    global award_word_dict

    print("Now gathering winner for year: " + str(year) + "\n")

    timer = time.time()
    winners = {}

    key_words = ["win", "wins", "won"]
    basic_word_dict = ["a", "an", "for", "in", "by", "or", "-", ":", ","]
    ban_words = [
        "Gold",
        "Dan",
        "It",
        ".",
        "99",
        "B",
        "M",
        "Adele",
        "Home",
        "Variety",
        "Ann",
        "Go",
        "Z",
        "X",
        "W",
        "A",
        "C",
        "D",
        "E",
        "Ben",
        "Les",
        "Jack",
        "Dani",
        "Lena",
        "Guide",
        "Jim",
        "H",
        "George",
        "S",
        "e",
        "Mis",
        "Lawrence",
        "Skyfall",
        ",",
        "AM",
        "all",
        "Waltz",
        "Lewis",
        "s",
        "z",
        "Carrie",
    ]

    f = "gg" + str(year) + ".json"
    tweets = [nltk.word_tokenize(tweet) for tweet in getTweets(f, 100000)]

    actor_names = nameDictionary[str(year)]
    movie_names = movieDictionary[str(year - 1)]

    award_tweets = []
    for tweet in tweets:
        if len(set(award_word_dict).intersection(tweet)) > 3:
            award_tweets.append(tweet)

    for tweet in award_tweets:
        # There is win keyword present
        if len((set(key_words) & set(tweet))) > 0:
            full_tweet = tweet[0]
            candidate = ""
            award = ""
            for i in range(1, len(tweet)):
                full_tweet = full_tweet + " " + tweet[i]
                c = tweet[i - 1] + " " + tweet[i]
                if (c in actor_names) and (
                    i + 1 < len(tweet) and tweet[i + 1] in key_words
                ):
                    candidate = c
            if len(candidate) == 0:
                for m in movie_names:
                    if (
                        (m in full_tweet)
                        and (m not in ban_words)
                        and (
                            full_tweet[
                                full_tweet.index(m)
                                + len(m)
                                + 1 : full_tweet.index(m)
                                + len(m)
                                + 5
                            ]
                            in key_words
                        )
                    ):
                        candidate = m
                        break

            for a in OFFICIAL_AWARDS_1315:
                if a in full_tweet:
                    award = a
                    break

            if len(candidate) > 0 and len(award) > 0:
                winners[award] = candidate

    global WINNERS
    WINNERS = winners
    print("Winners Gathered! \n")
    print("Total runtime: %s seconds" % str(time.time() - timer))
    return winners


def get_presenters(year):
    """Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns."""
    presenters = {}
    print("Getting list of presenters for year: " + year + "\n")
    # ------ get json file
    f = "gg" + str(year) + ".json"

    # ------ get all tweets in a list
    tweets = getTweets(f, " ")

    # ------ get award names and populate dictionary
    if (year == "2013") or (year == "2015"):
        awards_for_func = OFFICIAL_AWARDS_1315

    elif (year == "2018") or (year == "2019"):
        awards_for_func = OFFICIAL_AWARDS_1819

    for award in awards_for_func:
        presenters[award] = []

    # ------ use re.findall to get a list of tweets that may have presenter names
    match_list = []
    for tweet in tweets:
        matches = re.findall(r"[Pp]resent?", tweet) or re.findall(
            r"[iI]ntroduce?", tweet
        )
        if matches != []:
            match_list.extend([tweet])

    # ------ get a list of key words
    kw = [
        "cecil",
        "drama",
        "actress",
        "actor",
        "comedy",
        "animated",
        "film",
        "foreign",
        "supporting",
        "director",
        "screenplay",
        "original",
        "song",
        "score",
        "television",
        "picture",
        "series",
        "musical",
    ]

    no_picture = ["foreign", "screenplay", "director"]

    # ------ loop through awards
    for award in awards_for_func:

        tokenizer = RegexpTokenizer(r"\w+")
        tokens = list(tokenizer.tokenize(award))
        same_words = list(set(tokens).intersection(kw))

        # ------ make substitutions
        if (
            "foreign" or "screenplay" or "director"
        ) in same_words and "picture" in same_words:
            if "picture" in same_words:
                same_words.remove("picture")

            if "picture" in same_words:
                same_words.append("movie")

        if "television" in same_words:
            same_words.append("tv")

        # ------ form regular expressions
        reg_exp = []
        for word in same_words:
            if word not in ["picture", "movie", "tv", "television", "series"]:
                regex = r"[" + word[0].lower() + word[0].upper() + "]" + word[1:] + "?"
                reg_exp.append(regex)

        # ------ use re.findall to get tweet matches
        # ------ several if clauses to make substitutions
        presenter_tweets = []

        for tweet in match_list:
            if "television" and "picture" in same_words:
                if (
                    all(re.findall(exp, tweet) for exp in reg_exp)
                    and (
                        re.findall(r"[Mm]ovie?", tweet)
                        or re.findall(r"[Pp]icture?", tweet)
                    )
                    and (
                        re.findall(r"[Tt]elevision?", tweet)
                        or re.findall(r"[Tt]v?", tweet)
                        or re.findall(r"[Tt]V?", tweet)
                        or re.findall(r"[Ss]eries?", tweet)
                    )
                ):
                    presenter_tweets.extend([tweet])

                elif "picture" in same_words:
                    if all(re.findall(exp, tweet) for exp in reg_exp) and (
                        re.findall(r"[Mm]ovie?", tweet)
                        or re.findall(r"[Pp]icture?", tweet)
                    ):
                        presenter_tweets.extend([tweet])

                elif "television" or "series" in same_words:
                    if all(re.findall(exp, tweet) for exp in reg_exp) and (
                        re.findall(r"[Tt]elevision?", tweet)
                        or re.findall(r"[Tt]v?", tweet)
                        or re.findall(r"[Tt]V?", tweet)
                    ):
                        presenter_tweets.extend([tweet])
            else:
                if all(re.findall(exp, tweet) for exp in reg_exp):
                    presenter_tweets.extend([tweet])

        # ------ get names in tweets
        common_names = []
        for tweet in presenter_tweets:
            match = re.findall(
                r"[A-Z][a-z]+,?\s+(?:[A-Z][a-z]*\.?\s*)?[A-Z][a-z]+", tweet
            )
            if match != []:
                common_names.append(match)

        # ------ remove stopwords
        new_list = []
        for name_lst in common_names:
            for name in name_lst:
                words = name.split()
                if all(word.lower() not in function_stopwords for word in words):
                    new_list.append(name)

        counter = Counter(new_list)
        counter = dict(counter.most_common(2))
        final_list = list(counter.keys())
        presenters[award] = final_list

    global PRESENTERS
    PRESENTERS = presenters
    print("Presenters Gathered! \n")
    # print(presenters)
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
    type, hosts=[], awards=[], nominees={}, winners={}, presenters={},
):
    # default to be official awards from what we gathered
    officialAwards = AWARDS

    output = None
    # if it is human readable or json, do something else
    if (type == "human") or (type == "Human"):
        output = ""
        # hosts if there is more than one
        output += "Host" + ("s: " if len(hosts) > 1 else ": ")
        # go through and grab the hosts
        for host in hosts:
            output += host + ", "
        # output
        output = output[:-2] + "\n\n"
        # AWARDS
        for i in range(len(officialAwards)):
            award = officialAwards[i]
            # generate the output for the awards
            output += "Award: " + award + "\n"
            # generate the output for the presenters
            output += "Presenters: " + "".join(
                [(str(pres) + ", ") for pres in presenters[award]]
            )
            # skip space
            output = output[:-2] + "\n"
            # generate the output for the nominees
            output += "Nominees: " + "".join(
                [(str(nom) + ", ") for nom in nominees[award]]
            )
            # skip space
            output = output[:-2] + "\n"
            # generate output for the winners
            output += "Winner: " + winners[award] + "\n\n"
        # return the output
        return output
    # generate the Json output if the request is made
    elif (type == "json") or (type == "JSON") or (type == "Json"):
        jsonOutput = {}
        jsonOutput["hosts"] = hosts
        jsonOutput["award_data"] = {}
        for i in range(len(officialAwards)):
            award = officialAwards[i]
            jsonOutput["award_data"][award] = {"THIS WILL BE FILLED OUT!!!"}
        # return the right output
        output = jsonOutput

    return output


# function that runs all of the code and returns in in a readable way
def runAllFunctions(year):
    global ALL_TWEETS
    ALL_TWEETS = getTweets("gg" + year + ".json", 150000)
    # can't actually do all tweets bc 2015 has like 1.7 million and that takes too long :)
    # run all of the functions
    get_hosts(year)
    get_awards(year)
    get_nominees(year)
    get_winner(year)
    get_presenters(year)
    # bestDressed = best_dressed(year)
    # worstDressed = worst_dressed(year)
    # output
    print("Generating output and output file...\n")
    # get the right year
    humanOutput = output("human", HOSTS, AWARDS, NOMINEES, WINNERS, PRESENTERS)
    # add this when it is done!!!!! :
    # {"Best Dressed": bestDressed, "Worst Dressed": worstDressed}
    # jsonOutput = output("json", HOSTS, WINNERS)
    """jsonOutput = output("json", HOSTS, AWARDS, NOMINEES, WINNERS, PRESENTERS)
    # create the json file
    with open("data" + str(year) + ".json", "w") as f:
        json.dump(jsonOutput, f)"""
    # print to the console
    print(humanOutput)
    return


### BONUS FUNCTIONS AND HELPERS ###


def best_dressed(year):
    # Get the right set of awards based on year
    global OFFICIAL_AWARDS
    if (year == "2013") or (year == "2015"):
        OFFICIAL_AWARDS = OFFICIAL_AWARDS_1315
    else:
        OFFICIAL_AWARDS = OFFICIAL_AWARDS_1819
    # tweets array
    global ALLTWEETS
    # print
    print("Gathering the list of best dressed attendees for year: " + year + "\n")
    stopwords = [
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
    ]
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
    matchingTweets = []
    for tweet in ALLTWEETS:
        # add to the matching tweet array of any of the words are the same
        if any(word in tweet for word in bestDressedKeywords):
            matchingTweets.append(tweet)

    result = []
    # ...
    # ...
    # ...
    return result


def worst_dressed(year):
    # define an array that will hold the right data
    global OFFICIAL_AWARDS
    # get the 2013, 2015, 2018, or 2019 data
    if (year == "2013") or (year == "2015"):
        OFFICIAL_AWARDS = OFFICIAL_AWARDS_1315
        print("Using OFFICIAL_AWARDS_1315 \n")
    elif (year == "2018") or (year == "2019"):
        OFFICIAL_AWARDS = OFFICIAL_AWARDS_1819
        print("Using OFFICIAL_AWARDS_1819 \n")
    else:
        ValueError("Please use data from 2013, 2015, 2018, or 2019!")
    # resulting array and tweets of interest
    result = []
    # ...
    # ...
    # ...
    return result


# run these before main
getTeamMembers()
pre_ceremony()

if __name__ == "__main__":
    # elapsedSeconds = seconds since 0
    elapsedSeconds = time.time()
    # run the function
    main()
    # run the helper functions with the given year
    year = sys.argv[1]
    runAllFunctions(year)
    # print the amount of time the program took
    print(time.time() - elapsedSeconds)
