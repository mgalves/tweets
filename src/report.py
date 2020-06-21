#!/usr/bin/python                                                                                                                                                                                        
# -*- coding: utf-8 -*-     
import os
import re
from unicodedata import normalize

import redis

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


def to_array(msg):
    """
    Gera um vetor canonico do texto
    """
    monogram = []
    canonic = msg.lower().decode("utf-8")
    canonic = re.sub("http://[^\s]+", "", canonic)
    canonic = re.sub("@[^\s]+", "", canonic)
    tokens = re.split("[\.\/:,;\?\!\-\(\)\s\'\"\>\<\[\]]", canonic)
    for i in range(0, len(tokens)-1):
        token = tokens[i]
        if token and len(token)>2 and token not in STOP_WORDS:
            # Salva monograma
            monogram.append(token)
    
    return monogram, tokens


def get_subsequences(tokens):
    """
    Gera subsequencias de tokens de cada tweet
    """
    list = []
    for i in range(0, len(tokens)-1):
        tmp = tokens[i]
        if len(tmp) <= 2 or tmp in STOP_WORDS:
            continue
        buf = [tokens[i]]
        for j in range(i+1, len(tokens)):
            tok = tokens[j]
            if tok:
                buf.append(tok) 
                if len(tok) > 2 and tok not in STOP_WORDS:
                    list.append(" ".join(buf))
            else:
                break

    return list
            

def find_sentences(token_vector):
    """
    Remove frase duplicadas e frases espurias
    token_vector: lista de listas de tokens
    """
    sequences = {}
    for tokens in token_vector:
        list = get_subsequences(tokens)
        for text in list:
            text = text.strip()
            if text in sequences:
                sequences[text] += 1
            else:
                sequences[text] = 1
    
    to_remove = []
    keys = [*sequences.keys()]
    for i in range(0, len(keys)-1):
        k1 = keys[i]
        if sequences[k1] <= 2:
            # Remove frases que aparecem apenas uma vez
            to_remove.append(k1)
            continue
    
        for j in range(i+1, len(keys)-1):
            k2 = keys[j]
            if sequences[k2] <= 2:
                # Remove frases que aparecem apenas uma vez
                to_remove.append(k2)
                continue
            
            if len(k1) > len(k2):
                # Se k1 contem k2 e k2 aparece menos vezes, remove k2
                if k1.find(k2) > -1:
                    if sequences[k1] >= sequences[k2]:
                        to_remove.append(k2)
                    else:
                        to_remove.append(k1)
            else:
                # Se k2 contem k1 e k1 aparece menos vezes, remove k1
                if k2.find(k1) > -1 :
                    if sequences[k2] >= sequences[k1]:
                        to_remove.append(k1)
                    else:
                        to_remove.append(k2)

    for tr in to_remove:
        try:
            del sequences[tr]
        except:
            pass
    return sequences


def parse_tweets(tweets):
    tokens_vector = []
    max_tokens = 0
    map_monogram = {}

    for tweet in tweets:
        monograms, tokens = to_array(tweet)
        tokens_vector.append(tokens)
        for word in monograms:
            if word in map_monogram:
                map_monogram[word] += 1
            else:
                map_monogram[word] = 1

    map_sentences = find_sentences(tokens_vector)
    return map_monogram, map_sentences


def merge(monograms, bigrams):
    list = []
    total = 0
    # Adiciona bigramas e a soma de todas as ocorrencias
    for bigram in bigrams:
        total += bigram[1]
        list.append(bigram)
    for monogram in monograms:
        for bigram in bigrams:
            if bigram[0].find(monogram[0]) > -1:
                break
        else:
            total += monogram[1]
            list.append(monogram)
    
    # Calcula frequencia de cada elemento
    for l in list:
        l[1] = float(l[1])/total

    return list    


def process_tweets(tweets, key):
    map_monogram, map_bigram = parse_tweets(tweets)
    total = 0
    l1 = [[k, v] for k, v in map_monogram.items()]
    l2 = [[k, v] for k, v in map_bigram.items()]
    l1 = sorted(l1, key=lambda x: x[1], reverse=True)[:20]
    l2 = sorted(l2, key=lambda x: x[1], reverse=True)[:20]
    list = merge(l1, l2)
    sorted_list = sorted(list, key=lambda x: x[1], reverse=True)[:20]
    return sorted_list


if __name__ == "__main__":
    redis = redis.Redis(host=os.getenv("REDIS_HOST"))
    print(redis.keys())
    # Obtem a lista dos temas salvos por ordem de ocorrencias
    keys = redis.zrange("dataset", 0, -1, withscores=True, desc=True)
    print(keys)
    
    for key, score in keys: # key - tema, score - numero de ocorrencias
        key = key.decode("utf-8") # Esse tal de UNICODE as vezes complica
        tweets = redis.lrange(f"set_{key}_tweets", 0, -1)
        topics = process_tweets(tweets, key)
        print("###############################################")
        print("###############################################")
        print(f"- TEMA {key}")
        print(f"- OCORRENCIAS {score}")
        print(topics)
