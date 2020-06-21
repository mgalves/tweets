#!/usr/bin/python
# -*- coding: utf-8 -*
import logging
import os
import re
from time import time

import redis
import simplejson
from celery import Celery
from celery.task import task
from dataset import load_dataset

MAX_OFFSET = 1000

DATASET = os.getenv("DATASET")
REDIS = redis.Redis(host=os.getenv("REDIS_HOST"))

LOGGER = logging.getLogger("processor")


app = Celery('tweets', broker=os.getenv("BROKER", ""))

########################################################################
########################################################################
########################################################################
########################################################################
# BLOCO DE INICIALIZACAO DE DADOS. O IDEAL EH ESTAR EM UM OBJETO
########################################################################
########################################################################
########################################################################
########################################################################
PATTERNS = {}
_, keywords_per_set = load_dataset(DATASET)

for dset, keywords in keywords_per_set.items():
    pattern = f"({'|'.join(keywords)})" # Constroe a regexp
    PATTERNS[dset] = re.compile(pattern, re.I) # Compula a regexp

print(PATTERNS)
########################################################################
########################################################################
########################################################################
########################################################################

@app.task
def parse_tweet(tweet_data):
    """
    Aqui acontece o trabalho sujo. Recebe um tweet e descobre a quem se refere
    """
    try:
        tweet = simplejson.loads(tweet_data)
        text = tweet['text']
        tweet_id = tweet['id']
        for key, pattern in PATTERNS.items():
            if pattern.search(text):
                # Achamos o conjunto a partir da regex. Agora vamos salvar algumas coisas
                pipe = REDIS.pipeline()
                pipe.zincrby("dataset", 1, key)
                pipe.incr("counter", 1)
                pipe.rpush(f"set_{key}_tweets", text)
                pipe.execute()
                print("TWEET", key, tweet_id)
                break

    except Exception as e:
        print("JSON PROCESSING ERROR", e)
