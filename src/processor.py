#!/usr/bin/python
# -*- coding: utf-8 -*
import logging
import os
import re
from time import time

import redis
import simplejson
import unicodedata
from celery import Celery
from celery.task import task
from dataset import load_dataset


DATASET = os.getenv("DATASET")

LOGGER = logging.getLogger("processor")

STOP_WORDS = ["a", "do", "e", "ter", "for", "pra", "pro", "no", "que", "sou", "vou", "vai", "assim"
              u"último",u"é",u"acerca",u"agora",u"algumas",u"alguns", u"será", "nesta", "neste",
              u"ali",u"ambos",u"antes",u"apontar",u"aquela",u"aquelas", "ainda", "tudo", "quero"
              u"aquele",u"aqueles",u"aqui",u"atrás",u"bem",u"bom","vai", "estava",
              u"cada",u"caminho",u"cima",u"com",u"como",u"comprido", "muito", "mais",
              u"conhecido",u"corrente",u"das",u"debaixo",u"dentro",u"desde", u"mim",
              u"desligado",u"deve",u"devem",u"deverá",u"direita",u"diz",
              u"dizer",u"dois",u"dos",u"e",u"ela",u"ele", u"dele", "assim", "falei"
              u"eles",u"em",u"enquanto",u"então",u"está",u"estão", "disse",
              u"estado",u"estar ",u"estará",u"este",u"estes",u"esteve", "estou",
              u"estive",u"estivemos",u"estiveram",u"eu",u"fará",u"faz",
              u"fazer",u"fazia",u"fez",u"fim",u"foi",u"fora", "hoje", "sou",
              u"horas",u"iniciar",u"inicio",u"ir",u"irá",u"ista", u"até",
              u"iste",u"isto",u"ligado",u"maioria",u"maiorias",u"mais", 
              u"mas",u"mesmo",u"meu",u"muito",u"muitos",u"nós", u"minha",
              u"não",u"nome",u"nosso",u"novo",u"o",u"onde", "sei", "isso", "deu",
              u"os",u"ou",u"outro",u"para",u"parte",u"pegar", u"nos", "levou",
              u"pelo",u"pessoas",u"pode",u"poderá", u"podia",u"por",u"porque",
              u"povo",u"promeiro",u"quê",u"qual",u"qualquer",u"quando",
              u"quem",u"quieto",u"saber",u"sem",u"ser", "vem", "=",
              u"seu",u"somente",u"têm",u"tal",u"também",u"tem", "somos", "fala",
              u"tempo",u"tenho",u"tentar",u"tentaram",u"tente",u"tentei",
              u"teu",u"teve",u"tipo",u"tive",u"todos",u"trabalhar",
              u"trabalho",u"tu",u"um",u"uma",u"umas",u"uns", "via", "aos",
              u"usa",u"usar",u"valor",u"ver",u"verdade", "sim", u"não", "nao",
              u"verdadeiro",u"você", "rt", "vs", "esse", "este", "essa", "esta"]


app = Celery('tweets', broker=os.getenv("BROKER", ""))


class ParserTask(app.Task):
    name = 'ParserTask'

    def __init__(self):
        """
        Inicializacao dos dados
        """
        self.PATTERNS = {}
        self.REDIS = redis.Redis(host=os.getenv("REDIS_HOST"))

        _, keywords_per_set = load_dataset(DATASET) 

        for dset, keywords in keywords_per_set.items():
            pattern = f"({'|'.join(keywords)})" # Constroe a regexp
            self.PATTERNS[dset] = re.compile(pattern, re.I) # Compula a regexp
        
        print(self.PATTERNS)

    def __parse_urls(self, key, urls):
        """
        Extract URL and add to sorted set
        """
        for url in urls:
            if url["expanded_url"].startswith("https://twitter.com/"):
                continue # Ignora URLS do Twitter
            self.REDIS.zincrby(f"urls_{key}", 1, url["expanded_url"])

    def __parse_hashtags(self, key, hashtags):
        """
        Extract hashtags and add to sorted set
        """
        for hashtag in hashtags:
            self.REDIS.zincrby(f"hashtags_{key}", 1, "#" + hashtag["text"])

    def __parse_mentions(self, key, mentions):
        """
        Extract mentions and add to sorted set
        """
        for mention in mentions:
            self.REDIS.zincrby(f"mentions_{key}", 1, "@" + mention["screen_name"])

    def __parse_tweet(self, key, tweet):
        canonic = unicodedata.normalize('NFKD', tweet.lower())
        canonic = re.sub("http://[^\s]+", "", canonic)
        canonic = re.sub("https://[^\s]+", "", canonic)
        canonic = re.sub("@[^\s]+", "", canonic)
        canonic = re.sub("#[^\s]+", "", canonic)
        tokens = re.split("[\.\/:,;\?\!\-\(\)\s\'\"\>\<\[\]]", canonic)
        for token in tokens:
            if len(token)>2 and token not in STOP_WORDS:
                self.REDIS.zincrby(f"wordcloud_{key}", 1, token)
        
    def __find_keys(self, text):
        for key, pattern in self.PATTERNS.items():
            if pattern.search(text):
                yield key

    def run(self, tweet_data):
        """
        Aqui acontece o trabalho sujo. Recebe um tweet e descobre a quem se refere
        """
        try:
            tweet = simplejson.loads(tweet_data)
            text = tweet['text']
            for key in self.__find_keys(text):
                self.REDIS.zincrby("dataset", 1, key)
                self.REDIS.incr("counter", 1)
                self.__parse_tweet(key, text)
                self.__parse_hashtags(key, tweet['entities']['hashtags'])
                self.__parse_urls(key, tweet['entities']['urls'])
                self.__parse_mentions(key, tweet['entities']['user_mentions'])

        except Exception as e:
            print("JSON PROCESSING ERROR", e)


app.tasks.register(ParserTask())
parse = app.tasks[ParserTask.name]


class PersistTask(app.Task):
    name = 'PersistTask'

    def __init__(self):
        self.output = open("dump.txt", "w")

    def run(self, tweet):
        self.output.write(tweet)
        self.output.flush()

app.tasks.register(PersistTask())
write = app.tasks[PersistTask.name]

