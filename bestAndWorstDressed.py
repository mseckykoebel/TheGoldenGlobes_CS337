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
