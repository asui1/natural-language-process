import nltk
from nltk.corpus import brown
from nltk.corpus import wordnet as wn
from nltk.corpus import cmudict
from nltk.stem import WordNetLemmatizer
import csv


#initialization needed for using WordNetLemmatizer and cmudict
stemmer = nltk.PorterStemmer()
pronunciations = cmudict.dict()
lemma = WordNetLemmatizer()

#return true if the word has more than one meaning
def is_homo(word):
    if(len(wn.synsets(word)) >1):
        return True
    return False

#return true if the word has more than one pronunciation
def is_hetero(word):
    if(word in pronunciations.keys()):
        if len(pronunciations[word])>1:
            return True
    return False

#return true if given word is a verb with no meaning such as be, do, have
def is_general(word):
    if(word == "was" or word == "been" or word == "are" or word == "did" or word == "are"
       or word == "is"or word == "be" or word == "have" or word == "had" or word == "has"
        or word == "were" or word == "am" or word == "do" or word == "does"):
        return True
    return False

#return number of pairs of homographs in given sentence words
def homo_counter(words):
    count = 0
    dups = []
    for i in range(len(words)-1):
        for j in range(i+1, len(words)):
            if words[i][2].lower() == words[j][2].lower() and words[i][1] != words[j][1] and words[i][2].lower() not in dups:
                dups.append(words[i][2].lower())
                count +=1
    return count

#return number of pairs of homographs with different parts-of-speech whether noun/verb/adj/adv
def part_of_speech(words):
    count = 0
    for i in range(len(words)-1):
        for j in range(i+1, len(words)):
            if words[i][2].lower() == words[j][2].lower() and words[i][3] == words[j][3]:
                count +=1
    return count

# for list shaped sentence line [a, dog], return then as connected form like "a dog"    
def print_sent(sentence):
    sen = ""
    for i in sentence:
        sen += i + " "
    return sen

# for the given tags with word_tokenize, return N for noun, V for verb, J for adjective, and R for adverb
def change_tag(tag):
    if(tag.startswith("NN")):
        return "N"
    if(tag.startswith("V")):
        return "V"
    if(tag.startswith("JJ")):
        return "J"
    if(tag.startswith("RB")):
        return "R"
    return False

# for four types of tag, N(noun), V(verb), J(adjective), R(adverb), return them in wordnet format
def tag_to_wn(tag):
    if(tag == "N"):
        return wn.NOUN
    if(tag == "V"):
        return wn.VERB
    if(tag == "J"):
        return wn.ADJ
    if(tag == "R"):
        return wn.ADV

#initialize list for saving all datas
sent = []
initial = []

#choose categories to be chosen
category = ['editorial', 'news', 'reviews']

#loop for each categories in above list category
for cat in category:
    
    #loop for sentences in given sentences
    for tagged_sent in brown.sents(categories=[cat]):

        #initialize data structure for homographs and heteronyms
        homo_sent =[]
        hetero_sent = []
        homo_count = 0
        hetero_count = 0

        #loop for every word in sentence
        for i in tagged_sent:

            #tokenize the word and save [word, pos_tag] as list format in variable data
            text = nltk.word_tokenize(i)
            data = list(nltk.pos_tag(text)[0])

            #sort given pos_tag and save its simplified version in variable tag
            tag = change_tag(data[1])

            #case the word is wanted form(noun, verb, adjective, adverb)
            if(tag != False):

                #add lemmatized version of word and simplified position tag to list
                #list data has [original word, position tag, lemmatized word, simplified position tag]
                data.append(lemma.lemmatize(data[0], pos = tag_to_wn(tag)))
                data.append(tag)

                #check if word has multiple meanings and is not be, have, do, etc... 
                if(is_homo(data[0]) and is_general(data[0]) == False):

                     #save words with multiple meanings
                     homo_sent.append(data)
                     homo_count +=1

                     #check for heteronyms 
                     if(is_hetero(data[0])):

                         #save words with heteronyms.
                         hetero_sent.append(data)
                         hetero_count += 1
                         
        #in list of words with multiple meaning, count words that occur more than once with different position tag
        homo_count = homo_counter(homo_sent)

        #get first 30 sentences
        if(len(initial)<30):
            #count number of different parts of speech
            parts = part_of_speech(homo_sent)

            #add all data to list sent
            initial.append([tagged_sent, homo_sent, hetero_sent, homo_count, hetero_count, parts, cat])
            
        #case where homographs exist
        if(homo_count >0):

            #count number of different parts of speech
            parts = part_of_speech(homo_sent)

            #add all data to list sent
            sent.append([tagged_sent, homo_sent, hetero_sent, homo_count, hetero_count, parts, cat])
    
# return priority of given element in list sent
def takeObj(elem):
    return 10000*elem[3] + 1000*elem[4] + 100*elem[5]+100 - len(elem[0])

#part for saving data in csv file
f = open('CS372_HW3_output_20160632.csv', 'w', newline = '')
wr = csv.writer(f)
wr.writerow(["initial 30 sentences"])

#check given word word is in given list words
def in_list(word, words):
    for i in words:
        if word == i[0]:
            return True
    return False

#get list of words in sentence and heteronyms and return string in with word's pronunciation
def print_result(sent, heteros):
    result = ""
    for i in sent:
        result += i + " "
        for j in heteros:
            if i == j[0]:
                p = pronunciations[j[0]]
                if j[1].startswith("V"):
                    result += "( " +print_sent(p[1])+ " ) "
                else:
                    result += "( " +print_sent(p[0])+ " ) "
                heteros.remove(j)
                break
                    
    return result

#print initial 30 sentences
for i in range(len(initial)):
    wr.writerow([str(i+1) + ". " + print_result(initial[i][0], initial[i][2])])
    wr.writerow(["Brown Corpus category: " + initial[i][6]])
    wr.writerow([" "])
wr.writerow([" "])
wr.writerow([" "])
wr.writerow([" "])


#sort all lists with given priority and get first 30 in order
sent.sort(key = takeObj, reverse = True)
rank = sent[:30]

#print ranked 30 sentences
wr.writerow(["ranked 30 sentences"])
for i in range(len(rank)):
    wr.writerow([str(i+1) + ". " + print_result(rank[i][0], rank[i][2])])
    wr.writerow(["Brown Corpus category: " + rank[i][6]])
    wr.writerow([" "])



f.close()

