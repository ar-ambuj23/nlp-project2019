import nltk
import re
import spacy
import inflect
import gender_guesser.detector as gender

nlp = spacy.load("en_core_web_lg")
inflect = inflect.engine()
gender_guess = gender.Detector(case_sensitive=False)


#   Commonly occurring pronouns and if they are plural/singular or gendered
male = ['he', 'him', 'his', 'man', 'men']
female = ['she', 'her', 'hers', 'woman', 'women']
cogender = ['we', 'they', 'us', 'them', 'our', 'their', 'ours', 'theirs']
nongender = ['i', 'me','it', 'its','they']
pronoun_male = ['he', 'him', 'his']
pronoun_female = ['she', 'her', 'hers']
org = ['us', 'them', 'our', 'their', 'ours', 'theirs']
person = ['i', 'me']
male_title = ['Mr','Sir','Mr.','Sir.']
female_title = ['Miss','Ms','Mrs','Miss.','Ms.','Mrs.']
nongender_titles =['Dr', 'Prof','Dr.', 'Prof.']

plural = ['we', 'they', 'us', 'them', 'our', 'their', 'ours', 'theirs', 'men', 'women', 'ladies', 'gentlemen']
singular = ['he', 'him', 'his', 'man', 'she', 'her', 'hers', 'woman', 'they', 'us', 'them', 'their',
            'theirs', 'that', 'it', 'there']


##
#   Class to store cluster heads that we are trying to co-reference
##
class Entity:
    def __init__(self, name, loc, xpos):
        self.name = name
        self.gender = 'unknown'
        self.entity = ''
        self.plural = 0
        self.corefs = {}
        self.location = loc
        self.occurances = []
        self.first_occurance = loc
        self.occurances.append(loc)
        self.x = xpos

    def change_name(self, new_name):
        self.name = new_name

    def change_gender(self, current_gender):
        self.gender = current_gender

    def change_entity(self, entity):
        self.entity = entity

    def change_plural(self, is_plural):
        self.plural = is_plural

    ##
    #   Add a reference to the cluster head and seeing if it provides new information about the cluster head
    ##
    def add_coref(self, name, location, xpos):
        head = establish_headnoun(name, location, xpos)

        if self.gender is 'unknown' and head.gender is not 'unknown':
            self.change_gender(head.gender)
        if self.entity is '' and head.entity is not '':
            self.change_entity(head.entity)
        if self.plural is 0 and head.plural is not 0:
            self.change_plural(head.plural)
        self.corefs[name] = head
        #   Add the location of the reference to the cluster head
        self.occurances.append(location)

    def print(self):
        fmt = '{:35} {:<35} {:<35} {:<35} {:<35}'
        print(fmt.format('Name: '+self.name, 'Location: '+str(self.location), 'Gender: '+self.gender,
                         'Entity: '+self.entity, 'Plural: '+str(self.plural)))


#   Tokenize and POS Tag the sentence
def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent


##
#   Get all the pronouns from the sentence
##
def hobbs_alg(string, num, reference_dict):
    sent = preprocess(string)
    possibilities = []

    #   Grammar used to create the noun Phrases
    grammar = r"""
    NP: {<PRP|PRP\$><NNS>}
    NP: { <PRP | PRP\$ >}
    """
    cp = nltk.RegexpParser(grammar)
    cs = cp.parse(sent)

    #   Remove unnecessary characters from the start of the string to more easily get NP out
    parse_tree = str(cs).strip('(S\n')
    noun_phrases = re.findall(pattern='\((NP[^)]+)', string=parse_tree)

    for np in noun_phrases:
        #   Removes the 'NP ' from the start of the string
        np = str(np[3:])
        np = np.split(' ')
        temp = []

        #   Remove the '/POS' from the word
        while '' in np:
            np.remove('')
        add = False
        for word in np:
            if 'PRP' in word or 'PRP$' in word:
                add = True
            temp.append(word[:word.index('/')])
        if add:
            possibilities.append(' '.join(word for word in temp))
    #   Creates and populates the headnoun dict
    #   find_coref()   Should be called once at the start of the pronoun search
    find_possible(possibilities, num, reference_dict)


##
#   Using the headnouns structure compare the pronouns and select the most likely cluster if one exists
##
def find_possible(possibilities, num, reference_dict):
    heads = list(headnouns.values())

    # Foreach pronoun compare set it's known fields and compare it to the cluster heads
    for pronoun in possibilities:
        #   Most likely head and which string it has closest to, but less than, the pronoun
        head = ''
        closest = 0

        #   Get baseline metrics for the pronoun
        split = pronoun.lower().split(' ')
        plurals = 0
        current_gender = 'unknown'
        if pronoun.lower() in singular:
            plurals = -1
        elif any(elem in split for elem in plural):
            plurals = 1
        if pronoun.lower() in male:
            current_gender = 'male'
        elif pronoun.lower() in female:
            current_gender = 'female'

        #   Foreach cluster head check if it is a possibility
        for hn in heads:
            if (hn.first_occurance < num) and  (plurals == hn.plural) and \
                    ((pronoun.lower() in male+female) and (hn.entity == 'PERSON') or (pronoun.lower in nongender and hn.entity == 'ORG')):
                    occ = list(hn.occurances)
                    for loc in occ:
                        if loc > num:
                            break
                        if loc >= closest:
                            closest = loc
                            head = hn


        #   Print the most likely head for the pronoun
        if head is not '':
            if head.x not in reference_dict:
                reference_dict[head.x] =[]
            reference_dict[head.x].append([head.name, num, pronoun, 0])



##
#   Takes a list of cluster heads and its corefrences and uses them to populate the head nouns corefernces
##
def find_coref(cluster_head_dict, reference_dict):
    for h in cluster_head_dict:
        head = establish_headnoun(cluster_head_dict[h][1], cluster_head_dict[h][0], h)
        headnouns[cluster_head_dict[h][1]] = head
        #   Add co-references
        if h in reference_dict:
            for ref in reference_dict[h]:
                headnouns[cluster_head_dict[h][1]].add_coref(ref[2], ref[1], h)


headnouns = {}


##
#   Given a cluster head and its location create an entity object and add it to the headnouns dictionary
##
def establish_headnoun(hn, loc, xpos):
    head = Entity(hn, loc, xpos)
    split = head.name.split(' ')
    doc = nlp(hn)
    for ent in doc.ents:
        head.change_entity(ent.label_)

    if head.entity is 'PERSON':
        if 'Mr.' in hn:
            head.change_gender('male')
        elif 'Ms.' in hn or 'Miss' in hn or 'Mrs.' in hn:
            head.change_gender('female')
        else:
            split = head.name.split(' ')
            if any(gender_guess.get_gender(elem) for elem in split):
                for i in range(0, len(split)):
                    if gender_guess.get_gender(split[i]) is not 'unknown':
                        head.change_gender(gender_guess.get_gender(split[i]))
                        break
        head.change_plural(-1)
    elif head.entity is 'ORG':
        head.change_plural(-1)
    elif not any(inflect.singular_noun(elem) for elem in split):
        head.change_plural(-1)
    else:
        for i in hn.split(' '):
            if inflect.singular_noun(i):
                head.change_plural(1)
    return head

def handle_pronouns(cluster_head_dict,pronoun,lineNum,file_lines,reference_dict):
    heads = []
    permX=-1
    for head in cluster_head_dict:
        if cluster_head_dict[head][1] is not pronoun:
            heads.append(cluster_head_dict[head][1])
        else:
            xNum = head
    for i in range(lineNum, len(file_lines)):
        s = re.sub('<COREF .+?>.+?<.+?>', '', file_lines[i])
        s = re.sub('<.+?>', '', s)

        referencer = -1
        words = s.split(' ')
        #ref = reference_dict[xNum]
        ref = [['I',6,'I']]
        if 'Dr' in s:
            x=0
        for word in words:
            if word is '':
                continue
            if referencer is -1:
                doc = nlp(word)
                if word in male_title+female_title+nongender_titles:
                    if word in male_title and pronoun in male:
                        index = words.index(word)+1
                        reference_dict[xNum].append([pronoun, i, words[index], 0])
                        referencer = words[index]
                    elif word in female_title and pronoun in female:
                        index = words.index(word)+1
                        referencer = words[index]
                    elif word in nongender_titles and pronoun not in plural:
                        index = words.index(word)+1
                        referencer = words[index]

            elif word ==referencer and (permX is xNum or permX is -1):
                if xNum not in reference_dict:
                    reference_dict[xNum]=[]
                reference_dict[xNum].append([pronoun, i, word, 0])
                permX=xNum

    return reference_dict

##
#   Takes a sentence and the sentence number and cleans it getting rid of the cluster heads and calls the algorithm
##
def entry(file_lines, cluster_head_dict, reference_dict):
    #   Compute the head noun and co-references for it
    find_coref(cluster_head_dict, reference_dict)
    num = 0
    pronoun_heads={}
    for x in cluster_head_dict:
        if cluster_head_dict[x][1].lower() in nongender:
                pronoun_heads[cluster_head_dict[x][1]] = cluster_head_dict[x][0]
                nongender.remove(cluster_head_dict[x][1].lower())

        elif cluster_head_dict[x][1].lower() in cogender:
            pronoun_heads[cluster_head_dict[x][1]] = cluster_head_dict[x][0]
            cogender.remove(cluster_head_dict[x][1].lower())

        elif cluster_head_dict[x][1].lower() in male:
            pronoun_heads[cluster_head_dict[x][1]] = cluster_head_dict[x][0]
            male.remove(cluster_head_dict[x][1].lower())

        elif cluster_head_dict[x][1].lower() in female:
            pronoun_heads[cluster_head_dict[x][1]] = cluster_head_dict[x][0]
            female.remove(cluster_head_dict[x][1].lower())

    remove =[]
    for s in file_lines:
        s = re.sub('<COREF .+?>.+?<.+?>', '', s)
        s = re.sub('<.+?>', '', s)
        for hn in pronoun_heads:
            if pronoun_heads[hn] is num:
                remove.append(hn)
        for word in remove:
            s=s.replace(word, '')
        hobbs_alg(s, num, reference_dict)
        num = num + 1
    for pronoun in remove:
        reference_dict = handle_pronouns(cluster_head_dict,pronoun,pronoun_heads[pronoun],file_lines,reference_dict)

    return reference_dict
