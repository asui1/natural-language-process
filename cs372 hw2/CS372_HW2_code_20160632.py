import nltk
from nltk.corpus import brown
from nltk.corpus import wordnet as wn
from nltk.corpus import sentiwordnet as swn
import csv

#list to add lists of words with their points
word_list = []


#traverse through words in list and return true if there is a set with same adverb, adjective set.
def check_dup(lis, word1, word2):
    for i in lis:
        if(i[0][0]==word1 and i[1][0]==word2):
            return True
    return False

#for given synset, add up all objective score using sentiwordnet and return it as a list
def append(word, synset):
    obj_count = 0
    for q in synset:
        swn_synset = swn.senti_synset(q.name())
        obj_count += swn_synset.obj_score()
    return [word, obj_count]

def process(sentence):
    j = 0
    #find case of 5 words that is VERB/BE VEB + PREPOSITION + ARTICLE + ADVERB + ADJECTIVE
    for (w1, t1), (w2, t2), (w3, t3), (w4, t4), (w5, t5) in nltk.ngrams(sentence, 5):
        if((t1.startswith('V') or t1.startswith('BE')) and (t2 == 'IN' or t2 == 'TO') and t3=='AT' and t4=='RB' and t5.startswith('JJ')):

            #set empty list temp
            temp = []

            #get synset of ADVERB(w4) and append list to temp by using append()
            synset = wn.synsets(w4, pos = 'r')
            temp.append(append(w4, synset))

            #get synset of ADJECTIVE(w5) and append list to temp by using append()
            synset = wn.synsets(w5, pos = 'a')
            temp.append(append(w5, synset))

            #check whether ADVERB(w4), ADJECTIVE(w5) set is already in word_list, objective score of ADVERB is non-zero,
            #and ADVERB ends with 'ly' and append it if all conditions fit
            if(check_dup(word_list, w4, w5)==False and temp[0][1] != 0 and temp[0][0].endswith('ly')):
                word_list.append(temp)

    #find case of 4 words that is VERB/BE VEB + PREPOSITION/ARTICLE + ADVERB + ADJECTIVE
    for (w1, t1), (w2, t2), (w3, t3), (w4, t4) in nltk.ngrams(sentence, 4):
        if((t1.startswith('V') or t1.startswith('BE')) and (t2 == 'IN' or t2 == 'TO' or t2 =='AT') and t3=='RB' and t4.startswith('JJ')):

            #set empty list temp
            temp = []

            #get synset of ADVERB(w3) and append list to temp by using append()
            synset = wn.synsets(w3, pos = 'r')
            temp.append(append(w3, synset))

            #get synset of ADJECTIVE(w4) and append list to temp by using append()
            synset = wn.synsets(w4, pos = 'a')
            temp.append(append(w4, synset))


            #check whether ADVERB(w3), ADJECTIVE(w4) set is already in word_list, objective score of ADVERB is non-zero,
            #and ADVERB ends with 'ly' and append it if all conditions fit
            if(check_dup(word_list, w3, w4)==False and temp[0][1] != 0 and temp[0][0].endswith('ly')):
                word_list.append(temp)

    #find case of 3 words that is VERB/BE VEB + ADVERB + ADJECTIVE
    for (w1, t1), (w2, t2), (w3, t3) in nltk.ngrams(sentence, 3):
        if((t1.startswith('V') or t1.startswith('BE'))and t2=='RB' and t3.startswith('JJ')):

            #set empty list temp
            temp = []

            #get synset of ADVERB(w2) and append list to temp by using append()
            synset = wn.synsets(w2, pos = 'r')
            temp.append(append(w2, synset))


            #get synset of ADJECTIVE(w3) and append list to temp by using append()
            synset = wn.synsets(w3, pos = 'a')
            temp.append(append(w3, synset))

            #check whether ADVERB(w3), ADJECTIVE(w4) set is already in word_list, objective score of ADVERB is non-zero,
            #and ADVERB ends with 'ly' and append it if all conditions fit
            if(check_dup(word_list, w2, w3)==False and temp[0][1] != 0 and temp[0][0].endswith('ly')):
                word_list.append(temp)

#for tagged sents in brown corpus, do function process, which makes word list of following element format
#[[ADVERB, objective point], [ADJECTIVE, objective point]]
for tagged_sent in brown.tagged_sents():
    process(tagged_sent)

#for element in list given return ADVERB's objective point from a element shaped like above
def takeObj(elem):
    return elem[0][1]+elem[1][1]

#sort word_list by ADVERB's objective score, ascending order
word_list.sort(key=takeObj)

answer = word_list[:100]

#these codes write ADVERB, ADJECTIVE set in order.
#first column is ADVERB, second column is ADJECTIVE.
f = open('CS372_HW2_output_20160632.csv', 'w', newline = '')
wr = csv.writer(f)
for i in range(100):
    wr.writerow([i+1, answer[i][0][0], answer[i][1][0]])
f.close()


