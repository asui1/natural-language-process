import nltk
import nltk.book as book
from nltk.corpus import wordnet as wn
import csv


"""make 4 lists of intensity-modifying adverbs with
similar meanings as defined in report"""

totally = ['extremely', 'completely', 'absolutely', 'almost', 'utterly', 'totally']

very = ['really', 'rather', 'hugely', 'immensely', 'very']

quite = ['pretty', 'fairly', 'just', 'enough', 'reasonably']

slightly = ['slightly', 'bit', 'few']

"""list for saving results"""
final_text = []

"""in c, it saves locations of words,
which enables to look exact position near a word."""
text7 = book.text7
c = nltk.ConcordanceIndex(text7.tokens, key = lambda s: s.lower())


"""for intensity-modifying adverbs in totally list,
find following words that comes after it and save them at save_text

for follwing words in save text, find synonyms with verb-form meaning.

for multiple lists of synonyms with different meanings,
if representative word(word at first) of meaning
is different word than original word (not [support, supports] or [write, wrote])
, then add it to final_text and go to next following word.

If no case, then find first different word from list with most synonyms"""

for i in totally:    
    save_text=[text7.tokens[offset+1] for offset in c.offsets(i)]
    for j in save_text:
        max_text = []
        for synset in wn.synsets(j, pos = wn.VERB):
            word_list = synset.lemma_names()
            if(word_list[0][:2] != j[:2]):
                if([j, word_list[0], "totally"] not in final_text):
                    final_text.append([j, word_list[0], "totally"])
                max_text = []
                break
            if(len(max_text) < len(word_list)):
                max_text = word_list
        if (len(max_text)>1):
            for k in max_text:
                if(k[:2] != j[:2]):
                    if([j, k, "totally"] not in final_text):
                        final_text.append([j, k, "totally"])
                    break

"""do the same for list very"""

for i in very:
    save_text=[text7.tokens[offset+1] for offset in c.offsets(i)]
    for j in save_text:
        max_text = []
        for synset in wn.synsets(j, pos = wn.VERB):
            word_list = synset.lemma_names()
            if(word_list[0][:2] != j[:2]):
                if([j, word_list[0], "very"] not in final_text):
                    final_text.append([j, word_list[0], "very"])
                max_text = []
                break
            if(len(max_text) < len(word_list)):
                max_text = word_list
        if (len(max_text)>1):
            for k in max_text:
                if(k[:2] != j[:2]):
                    if([j, k, "very"] not in final_text):
                        final_text.append([j, k, "very"])
                    break

"""do the same for list quite"""

for i in quite:
    save_text=[text7.tokens[offset+1] for offset in c.offsets(i)]
    for j in save_text:
        max_text = []
        for synset in wn.synsets(j, pos = wn.VERB):
            word_list = synset.lemma_names()
            if(word_list[0][:2] != j[:2]):
                if([j, word_list[0], "quite"] not in final_text):
                    final_text.append([j, word_list[0], "quite"])
                max_text = []
                break
            if(len(max_text) < len(word_list)):
                max_text = word_list
        if (len(max_text)>1):
            for k in max_text:
                if(k[:2] != j[:2]):
                    final_text.append([j, k, "quite"])
                    break

"""do the same for list slightly"""

for i in slightly:
    save_text=[text7.tokens[offset+1] for offset in c.offsets(i)]
    for j in save_text:
        max_text = []
        for synset in wn.synsets(j, pos = wn.VERB):
            word_list = synset.lemma_names()
            if(word_list[0][:2] != j[:2]):
                if([j, word_list[0], "slightly"] not in final_text):
                    final_text.append([j, word_list[0], "slightly"])
                max_text = []
                break
            if(len(max_text) < len(word_list)):
                max_text = word_list
        if (len(max_text)>1):
            for k in max_text:
                if(k[:2] != j[:2]):
                    if([j, word_list[0], "slightly"] not in final_text):
                        final_text.append([j, k, "slightly"])
                    break


""" print 50 results"""

f = open('CS372_HW1_output_20160632.csv', 'w', newline = '')
wr = csv.writer(f)
for i in range(50):
    wr.writerow([i+1, final_text[i][1], final_text[i][2] + "  " + final_text[i][0]])

f.close()
