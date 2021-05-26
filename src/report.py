#!/usr/bin/python                                                                                                                                                                                        
# -*- coding: utf-8 -*-     
import os
import re
import redis
from unicodedata import normalize


REDIS = redis.Redis(host=os.getenv("REDIS_HOST"))


if __name__ == "__main__":
    data = {}
    report = open("report.json", "w", encoding="utf-8")
    redis = redis.Redis(host=os.getenv("REDIS_HOST"))
    # Obtem a lista dos temas salvos por ordem de ocorrencias
    keys = redis.zrange("dataset", 0, -1, withscores=True, desc=True)
    for key, score in keys: # key - tema, score - numero de ocorrencias
        key = key.decode("utf-8") # Esse tal de UNICODE as vezes complica
        topics = redis.zrange(f"wordcloud_{key}", 0, -1, withscores=True, desc=True)
        hashtags = redis.zrange(f"hashtags_{key}", 0, -1, withscores=True, desc=True)
        mentions = redis.zrange(f"mentions_{key}", 0, -1, withscores=True, desc=True)
        urls = redis.zrange(f"urls_{key}", 0, -1, withscores=True, desc=True)

        data[key] = {
            "tweets": score,
            "topics": [(t.decode("utf-8"), s) for t, s in topics],
            "hashtags": [(t.decode("utf-8"), s) for t, s in hashtags],
            "mentions": [(t.decode("utf-8"), s) for t, s in mentions],
            "urls": [(t.decode("utf-8"), s) for t, s in urls]
        }

        print("###############################################")
        print("###############################################")
        print(f"- TEMA {key}")
        print(f"- HASHTAGS {hashtags}")
        print(f"- MENTIONS {mentions}")
        print(f"- URLS {urls}")
        print(f"- TOPICS {topics}")

        import json
        json.dumps(data)

    import json
    s = json.dumps(data)
    report.write(s)
    report.close()
