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
    for name in allData[1:len(allData)-1]:
        # get the name, birth date, and death date
        name_name = name[1]
        name_birth = name[2]
        name_death = name[3]

        # if we're missing data, continue
        if name_birth == '\\\\N':
            continue

        # check if they're still alive
        if name_death == '\\\\N':
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
            years_active = range(2010, years_active[-1]+1)
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
