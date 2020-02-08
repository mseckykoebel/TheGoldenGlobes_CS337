#!/usr/bin/env python
# required and not required
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
from helpers import getIMDbData
from helpers import getTeamMembers


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
OFFICIAL_AWARDS_2020 = None

### Defining program constants
AWARD_TOKEN_SET = set()
# possible keywords for the ceremoney itself
AWARD_KEYWORDS = ["#goldenglobes","goldenglobes2013","goldenglobes2015","golden globes","golden","globes","gg2013","gg2015","gg2020"]

# all of the names in the IMDb database are going to go here
nameDictionary = {}

def pre_ceremony():
    """This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns."""

    """Creates a tsv file of the names of all of the actors on the
    IMDb database, their birth and death year, primary profession, and"""

    global nameDictionary
    
    print("Beginning the pre-ceremoney process...")
    # TIMER START
    timer = time.time()

    f = getIMDbData()

    print("Processing data to nameDictionary (data.tsv cam be opened with excel")
    print("\n")

    f = gzip.open('nameBasics.tsv.gz')
    # read the file as strings
    dataContent = str(f.read())
    # split the content where there is a new line
    dataSeparators = dataContent.split('\\n')
    # split the lines with tab
    for line in dataSeparators:
        # all of the data will be in the array
        allData = []
        allData.append(line.split('\\t'))
    # only take names from 2012 - 2020 (assuming this is not tested earlier)
    for year in range(2012, 2020):
        nameDictionary[str(year)] = []

    # ignore the first and last line
    for name in allData[1:len(allData)-1]:
        # get the name, birth, and death fields
        actualActorName = name[1]
        actorBirthday = name[2]
        actorDeathDay = name[3]

        # if data in the table is missing, pass over it and move onto the next name
        if actorBirthday == '\\N':
            continue
        if actualActorName == '\\N':
            continue

        # check if they're still alive
        if actorDeathDay == '\\N':
            # object of all years the actor has been active, in order
            yearsActive = range(int(actorBirthday), 2020)
        else:
            yearsActive = range(int(actorBirthday), int(actorDeathDay) + 1)

        # check edge cases
        if yearsActive[0] < 2010 and yearsActive[-1] < 2010:
            continue
        if yearsActive[0] > 2020:
            continue
        if yearsActive[0] < 2010:
            yearsActive = range(2010, yearsActive[-1]+1)

        # add names to the data file, and not the other information
        for year in yearsActive:
            nameDictionary[str(year)].append(actualActorName)

    print("Pre-ceremony processing complete.")

    print("\n")

    # TIMER END
    print("Total runtime: %s seconds" % str(time.time() - timer))

    print("\n")

    return


def get_hosts(year):
    """Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns."""
    # Your code here
    return hosts


def get_awards(year):
    """Awards is a list of strings. Do NOT change the name
    of this function or what it returns."""
    # Your code here
    return awards


def get_nominees(year):
    """Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns."""
    # Your code here
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
    return presenters


def main():
    """This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns."""
    return

# run these before main
getTeamMembers()
pre_ceremony()

if __name__ == "__main__":
    # elapsedSeconds = seconds since 0
    elapsedSeconds = time.time()
    # run the function
    main()
    # print the amount of time the program took
    print(time.time() - elapsedSeconds)