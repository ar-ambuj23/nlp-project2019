import nltk
import re
from nltk import Tree
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

#   Example string to get the NP from
ex = "That campaign, which included a strike, faltered when the company hired new workers and the International Meatpacking Union wrested control of the local union from Rogers' supporters."

#   Tokenize and POS Tag the sentence
def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent

def main():
    sent = preprocess(ex)

    #   Possible POS tags
    ###
    # CC coordinating conjunction
    # CD cardinal digit
    # DT determiner
    # EX existential there (like: "there is" ... think of it like "there exists")
    # FW foreign word
    # IN preposition/subordinating conjunction
    # JJ adjective 'big'
    # JJR adjective, comparative 'bigger'
    # JJS adjective, superlative 'biggest'
    # LS list marker 1)
    # MD modal could, will
    # NN noun, singular 'desk'
    # NNS noun plural 'desks'
    # NNP proper noun, singular 'Harrison'
    # NNPS proper noun, plural 'Americans'
    # PDT predeterminer 'all the kids'
    # POS possessive ending parent's
    # PRP personal pronoun I, he, she
    # PRP$ possessive pronoun my, his, hers
    # RB adverb very, silently,
    # RBR adverb, comparative better
    # RBS adverb, superlative best
    # RP particle give up
    # TO to go 'to' the store.
    # UH interjection errrrrrrrm
    # VB verb, base form take
    # VBD verb, past tense took
    # VBG verb, gerund/present participle taking
    # VBN verb, past participle taken
    # VBP verb, sing. present, non-3d take
    # VBZ verb, 3rd person sing. present takes
    # WDT wh-determiner which
    # WP wh-pronoun who, what
    # WP$ possessive wh-pronoun whose
    # WRB wh-abverb where, when
    ###

    #   Grammar used to create the noun Phrases
    grammar = r"""
    NP: {<DT><NN|NNP|NNS|CD|NNPS*>+}          # Chunk sequences of DT, JJ, NN, NNP
    NP: {<NN|NNP|NNS|CD|NNPS*>+}
    NP: {<DT><NN*>+}
    """
    #   Creates the parse tree
    cp = nltk.RegexpParser(grammar)
    cs = cp.parse(sent)

    #   Remove unnecissary characters from the start of the string to more easily get NP out
    parse_tree = str(cs).strip('(S\n')

    phrases =[]
    noun_phrases=re.findall(pattern='\(([^)]+)', string=parse_tree)

    for np in noun_phrases:
        #   Removes the 'NP ' from the start of the string
        np =str(np[3:])
        np =np.split(' ')
        temp=[]

        #   Remove the '/POS' from the word
        for l in np:
            temp.append(l[:l.index('/')])
        phrases.append(' '.join(word for word in temp))
    print(phrases)
#   Calls the main method
main()