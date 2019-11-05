#!/usr/bin/env python
# coding: utf-8

# import nltk
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

from reader import *
from string_matching_by_word import *
from string_matching_by_spaCy_NP import *
from word_embeddings_by_spaCy_NP import *
from hobbs import entry
from nltk import pos_tag

import sys
import contextlib

import warnings
warnings.filterwarnings("ignore")

# ### Read Document

# input_path = '/Users/ambuj/Documents/MS Stuff/nlp_cs_6340/final_project/nlp-project2019/dev/{}.input'.format(file_number)
# key_path = '/Users/ambuj/Documents/MS Stuff/nlp_cs_6340/final_project/nlp-project2019/dev/{}.key'.format(file_number)


def driver(input_path_file, output_path):
    
    fileObj = open(input_path_file,'r')
    list_of_ip_path = fileObj.readlines()
    list_of_ip_path = list(map(lambda x: x.rstrip('\n'), list_of_ip_path))
    
    for input_path in list_of_ip_path:
        
        file_number = input_path.split('/')[-1].split('.')[0]
        
        print('Processing file {}.input...').format(file_number)
        
        read = ReadInput(input_path)
        list_of_sentences = read.getListOfSentences()
        full_text = read.getText()

        # ### Get Sentence Dict and Cluster Head Dict

        sentence_dict = getSentenceDict(list_of_sentences)
        cluster_head_dict = getClusterHeads(sentence_dict)

        # ### Get Coref for exact match by word

        coref_dict_match_word = getCorefDict_match_word(sentence_dict, cluster_head_dict,90)

        # ### Get Coref for threshold match by NP

        coref_dict_match_NP = getCorefDict_match_NP(sentence_dict, cluster_head_dict,80)

        # ### Get Coref for Word Embedding Similarity by NP

        coref_dict_all_sorted = getCorefDict_all_sorted(sentence_dict, cluster_head_dict,0.5)
        # coref_dict_max_sentence = getCorefDict_max_of_each_sentence(sentence_dict, cluster_head_dict,0.5)

        # coref_dict_all_sorted_top3 = get_TopN_Matches(coref_dict_all_sorted,3)

        # ### Merging coref_dict_match_NP with coref_dict_all_sorted_top3

        def mergeDicts(string_matching_dict, word_embedding_dict):

            d1 = string_matching_dict.copy()
            d2 = word_embedding_dict.copy()

            d1_keys = d1.keys()
            d2_keys = d2.keys()

            for key in d1_keys:
                d1[key] = list(map(lambda x: x[0:3], d1[key]))

            for key in d2_keys:
                d2[key] = list(map(lambda x: x[0:3], d2[key]))

            for key in d2_keys:
                if(key not in d1_keys):
                    d1[key] = d2[key]
                else:
                    for val in d2[key]:
                        if(val not in d1[key]):
                            d1[key].append(val)

            return d1


        coref_final = mergeDicts(coref_dict_match_NP, coref_dict_all_sorted)


        # ### Passing the reference dict to Hobbs

        coref_final_with_pro = entry(list_of_sentences, cluster_head_dict, coref_final)

        # ### Adding those Cluster Heads which were not predicted

        def addNOPredsClusterHeads(cluster_head_dict, coref_final_with_pro):
            for cluster_id, cluster_val in cluster_head_dict.items():
                if(cluster_id not in coref_final_with_pro.keys()):
                    coref_final_with_pro[cluster_id] = [['',int(cluster_val[0]),'', None]]

            return coref_final_with_pro

        coref_final_with_pro = addNOPredsClusterHeads(cluster_head_dict, coref_final_with_pro)

        # ### Removing the Determiners from the start

        def removeDetfromStart(coref_final_with_pro):
            for cluster in coref_final_with_pro.keys():
                for i in range(0, len(coref_final_with_pro[cluster])):
                    if(len(coref_final_with_pro[cluster][i][2].split(' '))>1):
                        ref_word_list = coref_final_with_pro[cluster][i][2].strip().split(' ')
                        ref_word_list = list(filter(bool, ref_word_list) )
                        check = pos_tag(ref_word_list)
                        if len(check) >1:
                            if 'DT' in check[0][1]:
                                sentence = ' '.join(coref_final_with_pro[cluster][i][2].split(' ')[1:])
                                coref_final_with_pro[cluster][i][2] = ' '.join(coref_final_with_pro[cluster][i][2].split(' ')[1:])

            return coref_final_with_pro

        coref_final_with_pro = removeDetfromStart(coref_final_with_pro)

        # ### Making no predictions for Pronouns (will be included in final version - Reverse Hobb's/ Trained Word Embedding model)

        def removePredsforPronouns(coref_final_with_pro):
            for cluster in coref_final_with_pro.keys():
                for i in range(0, len(coref_final_with_pro[cluster])):
                    curr_cluster_name = coref_final_with_pro[cluster][i][0].split(' ')
                    if(len(curr_cluster_name)==1 and curr_cluster_name[0]!=''):
                        if('PRP' in pos_tag(curr_cluster_name)[0]):
                            coref_final_with_pro[cluster] = []
                            break
            return coref_final_with_pro

        # In[396]:

        coref_final_with_pro = removePredsforPronouns(coref_final_with_pro)

        # ### Print Output

        def printOP(cluster_head_dict, coref_final_with_pro):

            for cluster_id, cluster_head_name in cluster_head_dict.items():

                print('<COREF ID="{}">{}</COREF>'.format(cluster_id, cluster_head_name[1]))

                coreferences = coref_final_with_pro[cluster_id]
                list_of_sent_ids = list(map(lambda x: x[1], coreferences))
                sorted_index_sent_ids = [i[0] for i in sorted(enumerate(list_of_sent_ids), key=lambda x:x[1])]
                coreferences = [coreferences[i] for i in sorted_index_sent_ids]

                for coref in coreferences:
                    if(coref[0] == ''):
                        continue
                    print('{{{0}}}'.format(coref[1]) + ' ' + '{' + coref[2] + '}')
                print('\n', end = '')      

        with open(output_path+'/{}.response'.format(file_number),'w') as f:
            with contextlib.redirect_stdout(f):
                printOP(cluster_head_dict, coref_final_with_pro)
        
        print('Output saved for file {}.input!').format(file_number)

            
if __name__ == "__main__":
    
    input_path_file = sys.argv[1]
    output_path = sys.argv[2]
    
    driver(input_path_file, output_path)
    