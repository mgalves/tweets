#!/usr/bin/python
# -*- coding: utf-8 -*
import os
import sys

import simplejson
from dataset import load_dataset
from processor import parse, write
from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener


class GrabberListener(StreamListener):
    def __init__(self):
        self.counter = 0

    """
    Processa recepcao de um tweet no socket HTTP
    """
    def on_data(self, data):
        """
        Tweet recebido. Vamos mandar para o processamento assincrono...
        """
        parse.delay(data)
        write.delay(data)
        print(self.counter)
        self.counter += 1
        return True

    def on_error(self, status):
        """
        Algo deu errado
        """
        print(f"Twitter Error {status}")
        return False


def grab_tweets(dataset):
    """
    Processo que escuta o socket HTTP do Streaming API e envia para processamento
    """
    TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY", "")
    TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET", "")
    TWITTER_ACCESS_KEY = os.getenv("TWITTER_ACCESS_KEY", "")
    TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "")

    print(f"DATASET {dataset}")

    keywords, _ = load_dataset(dataset)
 
    print(f"SEARCH PARAMS = {keywords}")

    auth = OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_KEY, TWITTER_ACCESS_SECRET)
    listener = GrabberListener()
    stream = Stream(auth, listener)
    stream.filter(track=keywords)
    print("Starting grabber...")


if __name__ == "__main__":
    try:
        dataset = os.getenv("DATASET")
        grab_tweets(dataset)
    except Exception as e:
        print(e)
