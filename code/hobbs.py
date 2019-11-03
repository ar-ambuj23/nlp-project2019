import nltk
import re
import spacy
import inflect
import gender_guesser.detector as gender

nlp = spacy.load("en_core_web_lg")
inflect = inflect.engine()
d = gender.Detector(case_sensitive=False)

male = ['he','him','his','man','men']
female = ['she','her','hers','woman','women']
cogender =['we', 'they', 'us','them','our','their','ours', 'theirs']
nogender =['it', 'its']

plural = ['we', 'they', 'us','them','our','their','ours', 'theirs','men','women','ladies','gentlemen']
singular = [ 'he','him','his','man', 'she','her','hers','woman','we', 'they', 'us','them','our','their','ours', 'theirs']
#   Class to store headnouns that we are trying to coreference
class Entity:

    def __init__(self, name,loc):
        self.name = name
        self.gender = 'unknown'
        self.entity=''
        self.plural = 0
        self.corefs = {}
        self.location = loc
        self.last_occurance = loc
        self.first_occurance = loc

    def change_name(self, new_name):
        self.name = new_name

    def change_gender(self, gender):
        self.gender = gender

    def change_entity(self, entity):
        self.entity = entity

    def change_plural(self, plural):
        self.plural = plural

    def add_coref(self, name, location):
        head = establish_headnoun(name,location)
        if self.gender is 'unknown' and head.gender is not 'unknown':
            self.change_gender(head.gender)
        if self.entity is '' and head.entity is not '':
            self.change_entity(head.entity)
        if self.plural is 0 and head.plural is not 0:
            self.change_plural(head.plural)
        self.corefs[name] = head
        if location > self.last_occurance:
            self.last_occurance = location
    def print(self):
        fmt = '{:35} {:<35} {:<35} {:<35} {:<35}'
        print(fmt.format('Name: '+self.name,'Location: '+str(self.location),'Gender: '+self.gender,'Entity: '+self.entity,'Plural: '+str(self.plural)))



#   Tokenize and POS Tag the sentence
def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent

#Get all the pronouns from the sentence
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
    NP: { <PRP | PRP\$ >}
    """
    #    NP: { < NN | PRP | PRP\$ | POS | NNP | NNS | CD | NNPS > + < IN > < NN | PRP | PRP\$ | POS | NNP | NNS | CD | NNPS > +}
    # NP: { < NN | PRP | PRP\$ | POS | NNP | NNS | CD | NNPS > +}
    # NP: { < PRP | PRP\$ | POS | NNP | NNS | CD | NNPS > + < NN >}
    # NP: { < NN | PRP | PRP\$ | POS | NNP | NNS | NNPS >}
    # NP: { < DT > < NN | PRP | PRP\$ | NNP | NNS | CD | NNPS > +}  # Chunk sequences of DT, JJ, NN, NNP
    # NP: {<NN|NNP|NNS|CD|NNPS*>+}
    # NP: {<DT><NN*>+}
    # NP: {<DT|JJ><NN|PRP|PRP$|NNP|NNS|CD|NNPS*>+}
    #   Creates the parse tree
    cp = nltk.RegexpParser(grammar)
    cs = cp.parse(sent)

    #   Remove unnecessary characters from the start of the string to more easily get NP out
    parse_tree = str(cs).strip('(S\n')
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
        for word in np:
            if 'PRP' in word or 'PRP$' in word:
                add = True
            temp.append(word[:word.index('/')])
        if(add):
            possibilities.append(' '.join(word for word in temp))
            add = False
    #   Creates and populates the headnoun dict
    find_coref()
    find_possible(possibilities)


def find_coref():
    hn = ['American Airlines', 'Mediation In Its Union Talks','pilots','flight attendants','The president'
         ,'the request for mediation','The union']
    loc = 0
    for h in hn:
        head =establish_headnoun(h,loc)
        headnouns[h]=head
        loc = loc+1
    for h in headnouns:
        headnouns[h].print()
    american = [('American Airlines unit',10),('the company',11),('American',11), ('the company',17),('the company',20)]
    pres  = [('Patt Gibs',14), ('President of the association',14), ('Ms. Gibbs',21)]
    for a in american:
        headnouns['American Airlines'].add_coref(a[0],a[1])
    for p in pres:
        headnouns['The president'].add_coref(p[0], p[1])


    #   Order
    heads = list(headnouns.values())
    heads.sort(key=lambda x: x.last_occurance, reverse=True)
    x=5


def find_possible(possibilities):
    print(possibilities)
    for pronoun in possibilities:
        pronoun=pronoun.lower()
        single = True
        gender = 'unknown'
        if pronoun not in singular:
            single = False
        if pronoun in male:
            gender ='male'
        elif pronoun in female:
            gender = 'female'
    return 0

headnouns={}
#Create a list of headnouns and their information
def establish_headnoun(hn,loc):

    head = Entity(hn,loc)

    doc = nlp(hn)
    for ent in doc.ents:
        head.change_entity(ent.label_)

    if(head.entity is 'PERSON'):
        if 'Mr.' in hn:
            head.change_gender('male')
        elif 'Ms.' in hn or 'Miss' in hn or 'Mrs.' in hn:
            head.change_gender('female')
        else:
            head.change_gender(d.get_gender(hn.split(' ')[0]))
        head.change_plural(-1)
    elif(head.entity is 'ORG'):
        head.change_plural(-1)
    else:
        for i in hn.split(' '):
            if inflect.singular_noun(i):
                head.change_plural(1)
    return head


#   Calls the main method
#   Example string to get the NP from
ex = "A possible complicating factor, however, is that the source of the precursor viruses may not be domestic poultry."
ex2 = "Since this ND virus reported from Victoria is almost identical to the 1999 Mangrove Mountain isolate, then it appears more than a remote probability that the same precursor virus(so-called Peat's Ridge strain) may have been present in these Victorian flocks for some time and a very similar mutation event has resulted in this virulent virus."
ex3 = "For countries or regions claiming ND freedom, this outbreak again underlines the need for continuous serosurveillance of poultry flocks with immediate epidemiological investigation (including attempts to isolate and classify any APMV-1 viruses circulating) at the first sign of seroconversion in flocks."
ex4 = "[Newcastle disease virus is a notoriously variable virus."
ex5 = 'The president of the Association of Professional Flight Attendants, which represents American\'s more than 10,000 flight attendants, called the request for mediation "premature" and characterized it as a bargaining tactic that could lead to a lockout.'
test ="Maggie Douglas said she saw her purse with their stuff and inside its been residing."
test1='A corporate campaign, she said, appeals to her members because "it is a nice, clean way to take a job action, and our women are hired to be nice.'
pronouns = 'I you he she it we they, me you her him it us them, my our your his her its their, mine ours yours his hers its theirs, '
def Main():
    hobbs_alg(test1)
    #   prp/$,


Main()
