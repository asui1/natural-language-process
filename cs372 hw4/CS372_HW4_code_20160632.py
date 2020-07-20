from Bio import Medline, Entrez
from random import randrange
import xlsxwriter
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import random
import csv

#sorting position tags for to make the tree.
grammar = r"""
NP: {<DT|JJ|NN.*>+}
PP: {<IN><NP>}
VP: {<VB.*><NP|PP>+$}
"""
#will make a tree with maximum depth of three
cp = nltk.RegexpParser(grammar, loop = 3)

#open downloaded datafile from medline
f = open('data_for_running_code.csv', 'r', newline = '')
rd = csv.reader(f)

#list to save all data from medline data
text = []

#to lemmatize word for its basic form
lemma = WordNetLemmatizer()

#5 words that I will search for
words = ['activate', 'inhibit', 'bind', 'accelerate', 'block']

#read all rows in datafile
#data file has tagged_sentence, PMID, year, organiziation, journal, title, sentence, and triples.
for row in rd:
    #for saving data without triples
    temp1 = []
    #to save triples
    temp2 = []
    
    for i in range(len(row)):
        if(i < 7):
            #add elements one by one.
            temp1.append(row[i])
        else:
            #since each triples have one column, put them is one list so that they are in single index
            if len(row[i]) > 3:
                
                temp2.append(row[i])

    #add all of them to list text
    temp1.append(temp2)
    text.append(temp1)

#randomly selected indexes for training and testing.
training = [80, 9, 56, 91, 94, 96, 4, 64, 49, 60, 51, 12, 17, 13, 57, 8, 90, 87, 20, 23, 32, 71, 86, 82, 48, 41, 6, 1, 34, 10, 84, 72, 58, 0, 16, 26, 65, 30, 25, 36, 61, 42, 75, 44, 99, 66, 79, 19, 92, 33, 15, 73, 31, 47, 29, 67, 77, 78, 85, 38, 7, 2, 27, 95, 63, 5, 46, 81, 40, 76, 45, 11, 88, 97, 35, 22, 50, 55, 62, 53]
test_int = [39, 89, 54, 43, 14, 28, 52, 3, 83, 21, 69, 74, 59, 68, 18, 98, 93, 70, 24, 37]

#list to save triples got by model
every_t = []

#list to save premade triples by hand
answers = []

#traverse through all datas
for i in range(100):
    #list to save triples of current sentence
    triples = []

    #tokenize sentence and put tags
    test = nltk.word_tokenize(text[i][6])
    data = list(nltk.pos_tag(test))

    #list for all appearances of wanted 5 verbs.
    verbs = []

    # for all words, find word with position tag of Verb
    for k in data:
        if k[1].startswith('V'):

            #check whether it's basic form is wanted verb and put it in list verbs if so.
            lem = lemma.lemmatize(k[0], pos = wn.VERB)
            if lem in words:
                verbs.append(k[0])

    #make tree of sentence
    parsed = cp.parse(data)

    #get premade triples and save them into list answers
    temp = (text[i][7][0].split(', '))
    ans = []
    for co in range(0, len(temp), 3):
        ans.append([temp[0], temp[1], temp[2]])
    answers.append(ans)

    #remove duplicate occurences of verb
    verbs = list(dict.fromkeys(verbs))

    #traverse through all verbs
    for v in verbs:
        verb_token = nltk.word_tokenize(v)[0]

        #initialize two nouns A and B and verb x to be searched
        found_noun1 = "None"
        found_noun2 = "None"
        found_verb = ""

        #boolean for whether verb should be got first before noun.
        wait_verb = False

        #traverse top of the tree
        for j in range(len(parsed)):

            #if jth element is a subtree
            if type(parsed[j]) is nltk.Tree:

                #traverse the subtree
                for k in range(len(parsed[j])):

                    #check the word is wanted word.
                    if str(verb_token) in str(parsed[j][k][0]):

                        #set found_verb to found verb.
                        found_verb = parsed[j][k][0]

                        #look for part after the verb in subtree to get 2nd noun B.
                        for q in range(k+1, len(parsed[j])):

                            #find for subtree with NP and get last word of NP
                            if(type(parsed[j][q]) is nltk.Tree):
                                if(parsed[j][q].label() == 'NP'):
                                    found_noun2 = parsed[j][q][-1][0]
                                    break
                                
                        #look before the verb of tree to get 1st noun A
                        for q in range(j-1, -1, -1):

                            #check wheather it is a tree
                            if(type(parsed[q]) is nltk.Tree):

                                #check that verb met a verb.
                                if(parsed[q].label() == 'VP'):
                                    wait_verb = False

                                #check verb need not to wiat a verb and subtree is NP or PP
                                if((parsed[q].label() == 'NP' or parsed[q].label() == 'PP') and not wait_verb):

                                    #get last word of NP
                                    if(parsed[q].label() == 'NP'):
                                        found_noun1 = parsed[q][-1][0]

                                    #get last word of PP, which is a noun
                                    else:
                                        found_noun1 = parsed[q][-1][-1]

                                    #incase noun was in tuple, (word, position), change it to word.
                                    if(type(found_noun1) != str):
                                        found_noun1 = found_noun1[0]

                                    #if there's space in front check whether there's CC(and or or) infront making form of A1 and A2
                                    if(q-2 > -1):
                                        if(type(parsed[q-1])) is not nltk.tree:
                                            if str(parsed[q-1][1]) == 'CC' and type(parsed[q-2]) is nltk.Tree:

                                                #case where it found an extra A
                                                if(parsed[q-2].label() == 'NP'):

                                                    #add current A to list triples and set it as new.
                                                    if(found_noun1 != "None"):
                                                        triples.append([found_noun1, found_verb, found_noun2])
                                                    found_noun1 = parsed[q-2][-1][0]
                                    break
                                
                            #check for non subtree cases
                            else:

                                #if it meets CC, it needs to meet another verb before getting noun
                                if str(parsed[q][1]) == 'CC':
                                    wait_verb = True

                                #check that the verb got the verb.
                                if str(parsed[q][1]).startswith("V"):
                                    wait_verb = False

                        #add current triple to list triples and reset all variables.
                        triples.append([found_noun1, found_verb, found_noun2])
                        found_noun1 = "None"
                        found_verb = ""
                        found_noun2 = "None"
                        wait_verb = False
                            
            #jth element is not a subtree and check it is the verb we are looking for
            elif str(verb_token) == str(parsed[j][0]):

                #set found verb searching verb.
                found_verb = parsed[j][0]

                #look before the verb for noun.
                for q in range(j-1, -1, -1):

                    #check it is a subtree.
                    if(type(parsed[q]) is nltk.Tree):

                        #if its a VP, check it met a verb.
                        if(parsed[q].label() == 'VP'):
                            wait_verb = False

                        #if it meets NP and need not wait for verb, get noun.
                        if((parsed[q].label() == 'NP') and not wait_verb):

                            #get noun
                            found_noun1 = parsed[q][-1][0]

                            #check front of noun for A1 CC(and) A2 form.
                            if(q-2 > -1):
                                if not(type(parsed[q-1])) is nltk.tree.Tree:
                                    if str(parsed[q-1][1]) == 'CC' and type(parsed[q-2]) is nltk.Tree:

                                        #found the form so add the triple to list triples.
                                        if(parsed[q-2].label() == 'NP'):
                                            triples.append([found_noun1, found_verb, found_noun2])
                                            found_noun1 = parsed[q-2][-1][0]
                            
                            break

                    #check for nonsubtree cases
                    else:

                        #met a CC, and check it needs to meed a verb
                        if str(parsed[q][1]) == 'CC':
                            wait_verb = True

                        #meets a verb, and check it met verb
                        if str(parsed[q][1]).startswith("V"):
                            wait_verb = False

                #look after the verb for B
                for q in range(j+1, len(parsed)):

                    #if found NP
                    if(type(parsed[q]) is nltk.Tree):                        
                        if(parsed[q].label() == 'NP'):

                            #change found_noun2 as B
                            found_noun2 = parsed[q][-1][0]

                            #check for B1 CC(and) B2 form.
                            if(q+2 < len(parsed)):
                                if str(parsed[q+1][1]) == 'CC' and type(parsed[q+2]) is nltk.Tree:

                                    #found case of B1 CC B2, so add it to list triple.
                                    if(parsed[q+2].label() == 'NP'):
                                        triples.append([found_noun1, found_verb, found_noun2])
                                        found_noun2 = parsed[q+2][-1][0]
                            break

                #if we find two As, A1 and A2, B1 of first triple is left as None to change it 
                if len(triples) != 0:
                    if(triples[-1][1] == found_verb and triples[-1][2] == "None"):
                        triples[-1][2] = found_noun2
                if len(triples) > 1:
                    if(triples[-2][1] == found_verb and triples[-2][2] == "None"):
                        triples[-2][2] = found_noun2

                #add triple to list triples and initialize all variables.
                triples.append([found_noun1, found_verb, found_noun2])
                found_noun1 = "None"
                found_verb = ""
                found_noun2 = "None"
                wait_verb = False

    #add list of triples to every_t, saving nth sentences's triple at index n
    every_t.append(triples)

f.close()

#initialize performance checking values.
pre_train_total = 0
pre_train_hit = 0
pre_test_total = 0
pre_test_hit = 0
rec_train_total = 0
rec_train_hit = 0
rec_test_total = 0
rec_test_hit = 0

#during the loop check for number of corrects and total number of training data.
for i in training:

    #check training data's precision(correct and total)
    for j in every_t[i]:
        pre_train_total+= 1
        if (j in answers[i]):
            pre_train_hit += 1

    #check training data's recall(correct and total)
    for j in answers[i]:
        rec_train_total += 1
        if (j in every_t[i]):
            rec_train_hit += 1

#calculate precision, recall and f-score of training data
pre_train = pre_train_hit/pre_train_total
rec_train = rec_train_hit/rec_train_total
f1_train = 2*(pre_train*rec_train)/(pre_train+rec_train)

#during the loop check
for i in test_int:

    #check test data's precision(correct and total)
    for j in every_t[i]:
        pre_test_total+= 1
        if (j in answers[i]):
            pre_test_hit += 1

    #check test data's recall(correct and total)
    for j in answers[i]:
        rec_test_total += 1
        if (j in every_t[i]):
            rec_test_hit += 1

#calculate precision, recall, and f-score of test data
pre_test = pre_test_hit/pre_test_total
rec_test = rec_test_hit/rec_test_total
f1_test = 2*(pre_test*rec_test)/(pre_test+rec_test)


#create required csv file
g = open('CS372_HW4_output_20160632.csv', 'w', newline = '')
wr = csv.writer(g)

#print first two rows for performance results of training and testing.
wr.writerow(["precision train", pre_train, "recall train", rec_train, "f-score train", f1_train])
wr.writerow(["precision test", pre_test, "recall test", rec_test, "f-score test", f1_test])
wr.writerow([])

#indicate order of following components.
wr.writerow(["Sentence", "Expected Annotations", "PMID", "Year", "Journal title", "Organization"])

#first print training sentences
wr.writerow(["training"])
for i in training:
    wr.writerow([text[i][6], every_t[i], text[i][1], text[i][2], text[i][4], text[i][3]])
wr.writerow([])

#second print testing sentences.
wr.writerow(["testing"])
for i in test_int:
    wr.writerow([text[i][6], every_t[i], text[i][1], text[i][2], text[i][4], text[i][3]])

g.close()
