import nltk
import re
import spacy


#   Tokenize and POS Tag the sentence
def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent

def hobbs_alg(string):
    sent = preprocess(string)
    possibilities = []
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
    NP: {<PRP|PRP\$><NNS>}
    NP: {<PRP|><NNS>}
    NP: {<NN|PRP|PRP\$|POS|NNP|NNS|NNPS>}
    NP: {<NN|PRP|PRP\$|POS|NNP|NNS|CD|NNPS>+<IN><NN|PRP|PRP\$|POS|NNP|NNS|CD|NNPS>+}
    NP: {<NN|PRP|PRP\$|POS|NNP|NNS|CD|NNPS>+}
    NP: {<PRP|PRP\$|POS|NNP|NNS|CD|NNPS>+<NN>}
    NP: {<NN|PRP|PRP\$|POS|NNP|NNS|NNPS>}
    NP: {<DT><NN|PRP|PRP\$|NNP|NNS|CD|NNPS>+}          # Chunk sequences of DT, JJ, NN, NNP 
    """
    # NP: {<NN|NNP|NNS|CD|NNPS*>+}
    # NP: {<DT><NN*>+}
    # NP: {<DT|JJ><NN|PRP|PRP$|NNP|NNS|CD|NNPS*>+}
    #   Creates the parse tree
    cp = nltk.RegexpParser(grammar)
    cs = cp.parse(sent)

    #   Remove unnecessary characters from the start of the string to more easily get NP out
    parse_tree = str(cs).strip('(S\n')
    phrases =[]
    noun_phrases=re.findall(pattern='\((NP[^)]+)', string=parse_tree)

    for np in noun_phrases:
        #   Removes the 'NP ' from the start of the string
        np =str(np[3:])
        np =np.split(' ')
        temp=[]

        #   Remove the '/POS' from the word
        while ('' in np):
            np.remove('')
        add = False
        for l in np:
            if 'PRP' in l or 'PRP$' in l:
                add = True
            temp.append(l[:l.index('/')])
        phrases.append(' '.join(word for word in temp))
        if(add):
            possibilities.append(' '.join(word for word in temp))
            add = False
    print(phrases)
    find_coref([],phrases,possibilities)
    #   From here we should call what is going to Compare NP to Cluster Heads and try to match them

def find_coref(references, phrases,possibilities):
    hn = ['American Airlines', 'Mediation In Its Union Talks','pilots','flight attendants','The president'
          ,'the request for mediation','The union']
    print(possibilities)
    nlp = spacy.load("en_core_web_lg")
    for head in hn:
        doc = nlp(head)
        for ent in doc.ents:
            print(ent.text, ent.label_)

    for p in possibilities:
        index = phrases.index(p)
        check_plural=nltk.pos_tag(p.split())
        plural = False
        for pair in check_plural:
            if('PRP$' in pair):
                print('plural')
                plural = True


#   Calls the main method
#   Example string to get the NP from
ex = "A possible complicating factor, however, is that the source of the precursor viruses may not be domestic poultry."
ex2 = "Since this ND virus reported from Victoria is almost identical to the 1999 Mangrove Mountain isolate, then it appears more than a remote probability that the same precursor virus(so-called Peat's Ridge strain) may have been present in these Victorian flocks for some time and a very similar mutation event has resulted in this virulent virus."
ex3 = "For countries or regions claiming ND freedom, this outbreak again underlines the need for continuous serosurveillance of poultry flocks with immediate epidemiological investigation (including attempts to isolate and classify any APMV-1 viruses circulating) at the first sign of seroconversion in flocks."
ex4 = "[Newcastle disease virus is a notoriously variable virus."
ex5 = 'The president of the Association of Professional Flight Attendants, which represents American\'s more than 10,000 flight attendants, called the request for mediation "premature" and characterized it as a bargaining tactic that could lead to a lockout.'
test ="Maggie Douglas said she saw her purse with their stuff and inside its been residing."
test1='A corporate campaign, she said, appeals to her members because "it is a nice, clean way to take a job action, and our women are hired to be nice.'
def Main():
    hobbs_alg(test1)
    #   prp/$,
Main()