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

# from other files
from helpers import getTeamMembers
from helpers import getIMDbData
from getTweetText import getTweets
from difflib import SequenceMatcher

# from the other files
from gg_api import OFFICIAL_AWARDS_1315
from gg_api import OFFICIAL_AWARDS_1819

# some globals
OFFICIAL_AWARDS = None
ALL_TWEETS = {}
AWARD_TOKEN_SET = set()

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

# Begin
def bestDressed(year):
    # Get the right set of awards based on year
    global OFFICIAL_AWARDS
    if year == "2013" or year == "2015":
        print("get_hosts: Using 2013/2015 awards")
        OFFICIAL_AWARDS = OFFICIAL_AWARDS_1315
    else:
        print("get_hosts: Using 2018/2019 awards")
        OFFICIAL_AWARDS = OFFICIAL_AWARDS_1819

    global ALL_TWEETS
    stopwords = ["Golden Globes", "@GoldenGlobes", "#goldenglobes", "Hollywood"]
    keywords = [
        "beautiful", "great outfit", "best dress", "amazing dress",
        "great suit", "gorgeous", "looks amazing"
    ]
    result = []
    relevant_tweets = []
    for tweet in ALL_TWEETS:
        if any(word in tweet for word in keywords):
            relevant_tweets.append(tweet)
    best_dressed_people = __common_objects(relevant_tweets, 'PERSON', year)
    cleaned_dict = {}
    for person in best_dressed_people:
        if person in stopwords:
            continue
        k = __val_exists_in_keys(cleaned_dict, person)
        if k is None:
            cleaned_dict[person] = best_dressed_people[person]
        else:
            cleaned_dict[k] += best_dressed_people[person]
    c = Counter(best_dressed_people)
    if (len(c.most_common(1)) > 0):
        result = [person[0] for person in c.most_common(5) if person]
    else:
        print("no none was best dressed")
    print(result)
    return result


def worstDressed(year):
    # Get the right set of awards based on year
    global OFFICIAL_AWARDS
    if year == "2013" or year == "2015":
        print("get_hosts: Using 2013/2015 awards")
        OFFICIAL_AWARDS = OFFICIAL_AWARDS_1315
    else:
        print("get_hosts: Using 2018/2019 awards")
        OFFICIAL_AWARDS = OFFICIAL_AWARDS_1819

    global ALL_TWEETS
    stopwords = ["Golden Globes", "@GoldenGlobes", "#goldenglobes", "Hollywood"]
    keywords = [
        "worst outfit", "bad outfit", "worst attire", "looks ugly",
        "bad attire", "gross", "ugly", "ugly dress", "ugly suit"
    ]
    result = []
    relevant_tweets = []
    for tweet in ALL_TWEETS:
        if any(word in tweet for word in keywords):
            relevant_tweets.append(tweet)
    worst_dressed_people = __common_objects(relevant_tweets, 'PERSON', year)
    cleaned_dict = {}
    for person in worst_dressed_people:
        if person in stopwords:
            continue
        k = __val_exists_in_keys(cleaned_dict, person)
        if k is None:
            cleaned_dict[person] = worst_dressed_people[person]
        else:
            cleaned_dict[k] += worst_dressed_people[person]

    c = Counter(cleaned_dict)
    if (len(c.most_common(1)) > 0):
        result = [person[0] for person in c.most_common(5) if person]
    else:
        print("no none was badly dressed")
    return result

def __is_similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def __val_exists_in_keys(keys_list, val):
    for key in keys_list:
        if __is_similar(key.lower(), val.lower()) >= 0.65 or val.lower() in key.lower() or key.lower() in val.lower():
            return key
    return None

def __common_objects(tweets, type, year):
    """Performs natural language processing on tweets,
    and attempts to match tokens to people or works of art from IMDb
    """
    stopwords = ['this year', 'tonight']
    global ALL_TWEETS
    words = {}
    name_pattern = re.compile('[A-Z][a-z]*\s[\w]+')
    for tweet in tweets:
        if ALL_TWEETS[year][tweet] is None:
            ALL_TWEETS[year][tweet] = __nlp(tweet).ents
        for ent in ALL_TWEETS[year][tweet]:
            if ent.label_ in ['ORDINAL', 'CARDINAL', 'QUANTITY', 'MONEY', 'DATE', 'TIME']:
                continue
            cleaned_entity = ent.text.strip()
            if cleaned_entity.lower() in stopwords:
                continue
            if type == 'PERSON' and name_pattern.match(cleaned_entity) is None:
                continue
            if (type == 'PERSON' and ent.label_ == 'PERSON') or type == 'WORK_OF_ART':
                ents = tokenizer(cleaned_entity)
                tokens = set()
                for token in ents:
                    tokens.add(str(token).lower())
                intersect = tokens.intersection(AWARD_TOKEN_SET)
                if len(intersect) < int(len(tokens) / 2) or len(intersect) == 0:
                    if cleaned_entity in words:
                        words[cleaned_entity] += 1
                    else:
                        words[cleaned_entity] = 1
    return words

bestDressed("2015")