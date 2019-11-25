#!/usr/bin/env python
# coding: utf-8

# https://stackoverflow.com/questions/33289820/noun-phrases-with-spacy

import spacy
nlp1 = spacy.load("en_core_web_lg")

import re

def getRemText(sent_id, sentence_dict):
    rem_text = {}
    for sid in sentence_dict.keys():
        if(sid >= sent_id): 
            rem_text[sid] = sentence_dict[sid]
    sorted_rem_text = dict(sorted(rem_text.items(), key = lambda x:x[0]))
    return sorted_rem_text

def getCorefDict_meaning_NP(sentence_dict, coref_final_with_pro, threshold):
    
    for cluster in coref_final_with_pro.keys():

        if(coref_final_with_pro[cluster][0][2]==''):

            current_cluster_sent_id = coref_final_with_pro[cluster][0][1]


            current_cluster_head = nlp1(coref_final_with_pro[cluster][0][0])
            current_cluster_head_np = list(current_cluster_head.noun_chunks)

            if(len(current_cluster_head_np)==0):
                continue
            
#             current_cluster_head_headNoun = current_cluster_head_np[0][-1]

            remaining_text = getRemText(current_cluster_sent_id, sentence_dict)

            for sid, sentence in remaining_text.items():

                clean = re.compile('<COREF .*?>.*?</COREF>') ## removing all coref tags from the current sentence
                clean_sentence = re.sub(clean, '', sentence)

                doc = nlp1(clean_sentence)

                for np in doc.noun_chunks:

                    ## If the NP is a pronoun, ignore it. 
                    ## We are handling pronouns by Hobb's algorithm
                    if(len(np) == 1 and np[0].pos_ == 'PRON'):
                        continue

                    similarity = current_cluster_head_np[0].similarity(np)
                    if(similarity*100 > threshold):
                        
                        coref_final_with_pro[cluster][0][1] = sid
                        coref_final_with_pro[cluster][0][2] = np.text
                        coref_final_with_pro[cluster][0][3] = similarity*100   
    
    return coref_final_with_pro