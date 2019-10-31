import re


def getText(file_path):
    '''Reads the txt file and returns list of sentences'''
    fileObj = open(file_path,'r')
    list_of_sentences = fileObj.readlines()
    return list_of_sentences

def getSentenceDict(list_of_sentences):
    '''
    Takes list of sentences in the document as input
    Returns a dictionary of sentence ids as keys and sentence text as value
    '''
    sentence_dict = {}
    for sentence in list_of_sentences:
        sentence_id = re.findall(r'<S ID="(.+?)">', sentence)[0]
        sentence_dict[sentence_id] = re.findall(r'>(.+?)</S>', sentence)[0]
    return sentence_dict

def getClusterHeads(sentence_dict):
    '''
    Take the sentence_dict as input
        - sentence_dict is a dictionary of sentence ids as keys and sentence text as value
    Returns a dict of cluster heads
        - the key of the dict is the cluster id
        - the value is another dictionary
            - the key is sentence id
            - the value is the cluster head
    '''
    cluster_head_dict = {}
    for sentence_id, sentence in sentence_dict.items():
        list_of_cluster_heads = re.findall(r'<COREF (.+?)</COREF>', sentence)
        for cluster in list_of_cluster_heads:
            cluster_split = cluster.split('>')
            head_name = cluster_split[1]
            head_id = re.findall(r'ID="(.+?)"',cluster_split[0])[0]
            cluster_head_dict[head_id] = [sentence_id, head_name]
    return cluster_head_dict

list_of_sentences  = getText('/Users/ambuj/Documents/MS Stuff/nlp_cs_6340/final_project/nlp-project2019/dev/a8.input')

sentence_dict = getSentenceDict(list_of_sentences)
# print(sentence_dict['6'])

cluster_head_dict = getClusterHeads(sentence_dict)
# print(cluster_head_dict)