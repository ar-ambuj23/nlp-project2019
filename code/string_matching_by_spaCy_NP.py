#!/usr/bin/env python
# coding: utf-8

# https://stackoverflow.com/questions/33289820/noun-phrases-with-spacy

import spacy
nlp = spacy.load("en_core_web_sm")

from fuzzywuzzy import fuzz

import re

def getRemText(sent_id, sentence_dict):
    rem_text = {}
    for sid in sentence_dict.keys():
        if(sid >= sent_id): 
            rem_text[sid] = sentence_dict[sid]
    sorted_rem_text = dict(sorted(rem_text.items(), key = lambda x:x[0]))
    return sorted_rem_text

def getSimilarityScore(cluster_head_name,noun_phrase):
    ## When NP will be used, then partial_ratio will be used
    return fuzz.partial_ratio(cluster_head_name.lower(),noun_phrase.lower_)

def getCorefDict_match_NP(sentence_dict, cluster_head_dict, threshold):
    
    ## Initialise a coref_dict 
    coref_dict = {}
    
    for cluster_id, cluster_value in cluster_head_dict.items():

        current_cluster_sent_id = cluster_value[0]        
        current_cluster_head = cluster_value[1]
        
        ## Doing the partial NP match only when the no of words in the cluster head are more than 1. 
        if(len(current_cluster_head.split()) > 1):
            
            current_cluster_head = nlp(current_cluster_head)
            current_cluster_head_np = list(current_cluster_head.noun_chunks)
            ## Taking just the head noun in the current cluster head
            current_cluster_head_headNoun = str(current_cluster_head_np[0]).split()[-1]
        
            remaining_text = getRemText(current_cluster_sent_id, sentence_dict)

            for sid, sentence in remaining_text.items():

                clean = re.compile('<COREF .*?>.*?</COREF>') ## removing all coref tags from the current sentence
                clean_sentence = re.sub(clean, '', sentence)

                doc = nlp(clean_sentence)

                for np in doc.noun_chunks:

                    ## If the NP is a pronoun, ignore it. 
                    ## We are handling pronouns by Hobb's algorithm
                    if(len(np) == 1 and np[0].pos_ == 'PRON'):
                        continue

                    similarity_score = getSimilarityScore(current_cluster_head_headNoun,np)

                    if(similarity_score > threshold):
                        if(cluster_id not in coref_dict.keys()):

                            coref_dict[cluster_id] = [list([current_cluster_head, sid, np.text, similarity_score])]
                        else:
                            coref_dict[cluster_id].append(list([current_cluster_head, sid, np.text, similarity_score]))
    return coref_dict