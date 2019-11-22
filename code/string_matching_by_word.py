#!/usr/bin/env python
# coding: utf-8

# https://www.datacamp.com/community/tutorials/fuzzy-string-python
from fuzzywuzzy import fuzz
import string

import re
def getRemText(sent_id, sentence_dict):
    rem_text = {}
    for sid in sentence_dict.keys():
        if(sid >= sent_id): 
            rem_text[sid] = sentence_dict[sid]
    sorted_rem_text = dict(sorted(rem_text.items(), key = lambda x:x[0]))
    return sorted_rem_text

def getSimilarityScore(cluster_head_name,word):
    ## Not using sort_ratio because considering single words. 
    ## When NP will be used, them partial_ratio will be used
    return fuzz.ratio(cluster_head_name.lower(),word.lower())

def getCorefDict_match_word(sentence_dict, cluster_head_dict, threshold):
    
    ## Initialise a coref_dict 
    coref_dict = {}
    
    for cluster_id, cluster_value in cluster_head_dict.items():

        current_cluster_sent_id = cluster_value[0]        
        current_cluster_head = cluster_value[1]
        
        if(len(current_cluster_head.split()) == 1):
           
            remaining_text = getRemText(current_cluster_sent_id, sentence_dict)

            for sid, sentence in remaining_text.items():

                clean = re.compile('<COREF .*?>.*?</COREF>') ## removing all coref tags from the current sentence
                clean_sentence = re.sub(clean, '', sentence)
                clean_sentence = clean_sentence.translate(str.maketrans('', '', string.punctuation))

                for word in clean_sentence.split():

                    similarity_score = getSimilarityScore(current_cluster_head,word)
                    if(similarity_score > threshold):
                        if(cluster_id not in coref_dict.keys()):
                            coref_dict[cluster_id] = [list([current_cluster_head, sid, word, similarity_score])]
                        else:
                            coref_dict[cluster_id].append(list([current_cluster_head, sid, word, similarity_score]))
    return coref_dict

