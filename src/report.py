#!/usr/bin/python                                                                                                                                                                                        
# -*- coding: utf-8 -*-  
import json   
import os
import re
import redis
import sys
from datetime import datetime
from unicodedata import normalize


class MongoReport(object):
    def __init__(self, collection):
        from pymongo import MongoClient
        self.client = MongoClient(os.getenv("MONGODB_HOST"))
        self.db = self.client["tweets"]
        self.collection = self.db.get_collection(collection)

    def report(self):
        print(f"Collection: {self.collection.name}")
        print(f"Documents: {self.collection.estimated_document_count()}")

    def dump(self, dirname="", pagesize=10000):
        start = 0
        end = pagesize
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        counter = 0 
        total = self.collection.count_documents({})
        while counter < total:
            documents = []
            filename = f"mongo_{timestamp}_{start}_{end}.txt"
            print(filename, total, counter)
            f = open(os.path.join(dirname, filename), "w")
            cursor = self.collection.find({}).skip(start).limit(pagesize)
            documents = [document for document in cursor]
            f.write(json.dumps(documents))
            f.close()
            counter += len(documents)
            start += pagesize
            end += pagesize


class REDISReport(object):
    def __init__(self):
        self.REDIS = redis.Redis(host=os.getenv("REDIS_HOST"))

    def _read_data(self):
        data = {}
        # Obtem a lista dos temas salvos por ordem de ocorrencias
        keys = self.REDIS.zrange("dataset", 0, -1, withscores=True, desc=True)
        for key, score in keys: # key - tema, score - numero de ocorrencias
            key = key.decode("utf-8") # Esse tal de UNICODE as vezes complica
            topics = self.REDIS.zrange(f"wordcloud_{key}", 0, -1, withscores=True, desc=True)
            hashtags = self.REDIS.zrange(f"hashtags_{key}", 0, -1, withscores=True, desc=True)
            mentions = self.REDIS.zrange(f"mentions_{key}", 0, -1, withscores=True, desc=True)
            urls = self.REDIS.zrange(f"urls_{key}", 0, -1, withscores=True, desc=True)

            data[key] = {
                "tweets": score,
                "topics": [(t.decode("utf-8"), s) for t, s in topics],
                "hashtags": [(t.decode("utf-8"), s) for t, s in hashtags],
                "mentions": [(t.decode("utf-8"), s) for t, s in mentions],
                "urls": [(t.decode("utf-8"), s) for t, s in urls]
            }
        return data

    def dump(self, filename="redis.json"):
        f = open(filename, "w")
        data = self._read_data()
        s = json.dumps(data)
        f.write(s)
        f.close()
        
    def report(self):
        data = self._read_data()

        for key, value in data.items(): # key - tema, score - numero de ocorrencias
            print("###############################################")
            print("###############################################")
            print(f"- TEMA {key}")
            print(f"- HASHTAGS {value['hashtags']}")
            print(f"- MENTIONS {value['mentions']}")
            print(f"- URLS {value['urls']}")
            print(f"- TOPICS {value['topics']}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 report.py [redis | mongo] [dump | report]")
    else:
        source = sys.argv[1]
        op = sys.argv[2]

        if source not in ["redis", "mongo"] or op not in ["dump", "report"]:
            print("Usage: python3 report.py [redis | mongo] [dump | report]")

        if source == "redis":
            reporter = REDISReport()            
        elif source == "mongo":
            reporter = MongoReport(os.getenv("DATASET"))

        getattr(reporter, op)()
