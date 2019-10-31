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
        sentence_id = re.findall(r'<S ID=".+?">', sentence)[0].split('"')[1]
        sentence_dict[sentence_id] = re.findall(r'>(.+?)</S>', sentence)[0]
    return sentence_dict


list_of_sentences  = getText('/Users/ambuj/Documents/MS Stuff/nlp_cs_6340/final_project/nlp-project2019/dev/a8.input')

sentence_dict = getSentenceDict(list_of_sentences)
# print(sentence_dict['6'])