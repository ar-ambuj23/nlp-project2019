#!/usr/bin/env python
# coding: utf-8


# https://stackoverflow.com/questions/33289820/noun-phrases-with-spacy
import spacy
nlp = spacy.load("en_core_web_md")

import re

get_ipython().system('export SPACY_WARNING_IGNORE=W008')

def getRemText(sent_id, sentence_dict):
    rem_text = {}
    for sid in sentence_dict.keys():
        if(sid >= sent_id): 
            rem_text[sid] = sentence_dict[sid]
    sorted_rem_text = dict(sorted(rem_text.items(), key = lambda x:x[0]))
    return sorted_rem_text


def getCorefDict_max_of_each_sentence(sentence_dict, cluster_head_dict, threshold):
    '''
    This function gives the most matching word in each sentence for a given cluster head
    It returns a dictionary:
        - Key: Cluster_head_id
        - Value: list of (current_cluster_head_name, sid, np, similarity_score)
    '''
    
    ## Initialise a coref_dict 
    coref_dict = {}
    
    for cluster_id, cluster_value in cluster_head_dict.items():
        current_cluster_sent_id = cluster_value[0]        
        current_cluster_head = cluster_value[1]
        
        remaining_text = getRemText(current_cluster_sent_id, sentence_dict)

        for sid, sentence in remaining_text.items():
            clean = re.compile('<COREF .*?>.*?</COREF>') ## removing all coref tags from the current sentence
            clean_sentence = re.sub(clean, '', sentence)

            doc = nlp(clean_sentence)
            word_embedding_score_list_per_sentence = []
            
            for np in doc.noun_chunks:
                
                ## If the NP is a pronoun, ignore it. 
                ## We are handling pronouns by Hobb's algorithm
                if(len(np) == 1 and np[0].pos_ == 'PRON'):
                    continue
                
                similarity_score = nlp(current_cluster_head).similarity(np)
                
                               
                word_embedding_score_list_per_sentence.append(list([current_cluster_head, sid, np.text, similarity_score]))
            
            if(len(word_embedding_score_list_per_sentence) == 0):
                continue
            scores_list = list(map(lambda x: x[3], word_embedding_score_list_per_sentence))
            max_score = max(scores_list)
            max_index = scores_list.index(max_score)

            max_word_embedding_score_list_per_sentence = word_embedding_score_list_per_sentence[max_index]


            if(max_score > threshold):
                if(cluster_id not in coref_dict.keys()):
                    coref_dict[cluster_id] = max_word_embedding_score_list_per_sentence
                else:
                    coref_dict[cluster_id].append(max_word_embedding_score_list_per_sentence)

    return coref_dict


def getCorefDict_all_sorted(sentence_dict, cluster_head_dict, threshold):
    '''
    This function gives the all the matching words in the whole doc, in desc order, for a given cluster head
    It returns a dictionary:
        - Key: Cluster_head_id
        - Value: list of (current_cluster_head_name, sid, np, similarity_score)
    '''
    
    ## Initialise a coref_dict 
    coref_dict = {}
    
    for cluster_id, cluster_value in cluster_head_dict.items():
        current_cluster_sent_id = cluster_value[0]        
        current_cluster_head = cluster_value[1]
        
        remaining_text = getRemText(current_cluster_sent_id, sentence_dict)
        
        word_embedding_score_list_all_sentences = []

        for sid, sentence in remaining_text.items():
            clean = re.compile('<COREF .*?>.*?</COREF>') ## removing all coref tags from the current sentence
            clean_sentence = re.sub(clean, '', sentence)

            doc = nlp(clean_sentence)

            for np in doc.noun_chunks:
                
                ## If the NP is a pronoun, ignore it. 
                ## We are handling pronouns by Hobb's algorithm
                if(len(np) == 1 and np[0].pos_ == 'PRON'):
                    continue
                
                similarity_score = nlp(current_cluster_head).similarity(np)
                
                if(similarity_score > threshold):
                    word_embedding_score_list_all_sentences.append(list([current_cluster_head, sid, np.text, similarity_score]))
                                
                
        if(len(word_embedding_score_list_all_sentences) == 0):
            continue
        else:
            scores_list = list(map(lambda x: x[3], word_embedding_score_list_all_sentences))
            sorted_indices = [i[0] for i in sorted(enumerate(scores_list), key=lambda x:x[1], reverse=True)]
            sorted_word_embedding_score_list_all_sentences = [word_embedding_score_list_all_sentences[i] for i in sorted_indices]


        if(cluster_id not in coref_dict.keys()):
            coref_dict[cluster_id] = sorted_word_embedding_score_list_all_sentences
        else:
            coref_dict[cluster_id].append(sorted_word_embedding_score_list_all_sentences)         

    return coref_dict

def get_TopN_Matches(coref_dict_all_sorted,n):
    '''
    To get Top N word embeddings in the document per Cluster Head
    Modifies and returns coref_dict_all_sorted
    '''
    
    for cluster_id, word_embedding_list in coref_dict_all_sorted.items():
        coref_dict_all_sorted[cluster_id] = coref_dict_all_sorted[cluster_id][:n]
    
    return coref_dict_all_sorted