#!/usr/bin/python                                                                                                                                                                                        
# -*- coding: utf-8 -*-     
import os

import redis

if __name__ == "__main__":
    redis = redis.Redis(host=os.getenv("REDIS_HOST"))
    redis.flushdb()
