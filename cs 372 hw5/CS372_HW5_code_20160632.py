import math, csv
from bs4 import BeautifulSoup
import requests
from urllib import request
from nltk.corpus import brown, reuters, words, stopwords, treebank
from nltk import *
import nltk
import sys
from sklearn.preprocessing import StandardScaler


#check whether two words first and second are identical
#if * exist, check all other characters match.
def is_match(first, second):

    #return False for blank(not a single word)
    if " " in first or " " in second:
        return False

    #return False if length are different
    if len(first) != len(second):
        return False

    #check match for word with *, ignoreing *
    if "*" in first or "*" in second:
        match = 0
        for i in range(len(first)):
            if first[i] == second[i]:
                match += 1
        if match >= len(first)-1:
            return True

    #check two words are identical
    else:
        if first == second:
            return True
    return False

#find all positions of word in text
def find_ord(text, word):
    length = len(word)
    index = []

    #try matching all possible case in text.
    for i in range(len(text)-length):
        cur_word = text[i: i+length]
        if is_match(cur_word, word):
            index.append(i)
    return index

#check for word in text, check which nth index of occur is equal to wanted_pos
def get_nth(text, word, wanted_pos, occur):
    count = 1

    # check value in occur is same os wanted_pos
    for i in occur:
        if i == wanted_pos or i == wanted_pos +1 or i == wanted_pos - 1:
            return count
        count += 1
        
    return len(occur)


#chunk text using word_tokenize, pos_tag and ne_chunk.
def chunk_text(text):

    #split text into sentences
    sents = text.split(".")

    #remove empty sentence
    if "" in sents:
        sents.remove("")

    #put chunked sentences in chunk
    chunks = []    
    for sent in sents:
        token = nltk.word_tokenize(sent)
        tagged_token = pos_tag(token)
        tree = ne_chunk(tagged_token, binary=True)
        chunks.append(tree)
    return chunks


#chane all information got into a stardard form to be passed
def get_vars(text, info, Ppos, Pos, boo):

    #boo is whether the word is True or Not.
    #used for training.
    if boo == "TRUE":
        var = [0, 0, len(info[1]), Ppos, Pos, 1]
    else:
        var = [0, 0, len(info[1]), Ppos, Pos, 0]

    #keep count of nouns in sentence, nouns in paragraph, and number of words.
    sent_count = 0
    para_count = 0
    word_count = 0

    #traverser though all chunk. each value in i is sentence
    for i in range(len(chunk)):
        sent_count = 0
        for j in range(len(chunk[i])):

            #case for tree
            if type(chunk[i][j]) is nltk.tree.Tree:
                sent_count += 1
                para_count += 1

                #for every word in subtree, check it matches
                for k in chunk[i][j]:
                    if (is_match(k[0], info[0][0])):
                        word_count += 1
                        
                        #update variables if it can
                        if word_count <= info[2]:
                            var[0] = para_count
                            var[1] = sent_count

            #case for word
            else:
                #if the word is noun, check it matches.
                if chunk[i][j][1][0:2] == 'NN':
                    sent_count += 1
                    para_count += 1
                    if (is_match(chunk[i][j][0], info[0][0])):
                        word_count += 1
                        
                        #update variables if it can
                        if word_count <= info[2]:
                            var[0] = para_count
                            var[1] = sent_count
                    
                

    return var    

#save data for snippet and page
data_snippet = []
data_page = []

#read validation file
tsv_file = open("gap-validation.tsv")
read_tsv = csv.reader(tsv_file, delimiter="\t")
count = 0


for row in read_tsv:
    
    #skip first line, header
    if count == 0:
        count +=1
        continue

    #set up variables in row to use later
    prep = row[2].split(" ")
    Ppos = int(row[3])
    perA = row[4].split(" ")
    Apos = int(row[5])
    Aans = row[6]
    perB = row[7].split(" ")
    Bpos = int(row[8])
    Bans = row[9]
    url = row[10]

    #try to get information from given url. data from url is saved in Acount and Bcount
    for trial in range(3):
        try:
            html_content = requests.get(url, timeout=(3, 10)).text
            soup = BeautifulSoup(html_content, "lxml")
            soup = soup.prettify()
            Acount = soup.count(perA[0])
            Bcount = soup.count(perB[0])
            break
        except:
            Acount = 0
            Bcount = 0

    #find all position of preposition, nounA, and nounB.
    Pord = find_ord(row[1], prep[0])
    Aord = find_ord(row[1], perA[0])
    Bord = find_ord(row[1], perB[0])

    #make list with information that can be get from text for every word
    #[word, all positions of word, index for previous element to get wanted word]
    target = [prep, Pord, get_nth(row[1], prep[0], Ppos, Pord)]
    first = [perA, Aord, get_nth(row[1], perA[0], Apos, Aord)]
    second = [perB, Bord, get_nth(row[1], perB[0], Bpos, Bord)]

    #chunk text
    chunk = chunk_text(row[1])

    #make all data into shape of dataset wanted
    Avar = get_vars(row[1], first, Ppos, Apos, Aans)
    Bvar = get_vars(row[1], second, Ppos, Bpos, Bans)

    #add their IDs
    Avar.append(row[0])
    Bvar.append(row[0])

    #add current data to snippet
    data_snippet.append(Avar)
    data_snippet.append(Bvar)

    #update with values from url
    if(Avar[2] < Acount):
        Avar[2] = Acount
    if(Bvar[2] < Bcount):
        Bvar[2] = Bcount

    #add data to page
    data_page.append(Avar)
    data_page.append(Bvar)
    count+=1


tsv_file.close()

#with dataset, parse them into three lists, for x(variables), y(results), and IDs.
def get_x_y(data):
    x = []
    y = []
    names = []
    for i in data:
        nums = i[:-1]
        temp_data = [int(x) for x in nums]
        x.append(temp_data[0:5])
        y.append(temp_data[5])
        names.append(i[6])
    return x, y, names


#add two x of same ID into one line
def mergex(data):
    ret = []
    for i in range(0, len(data), 2):
        cur = data[i]
        cur.extend(data[i+1])
        ret.append(cur)
    return ret

#change two y of same ID to one line
#0 0 -> 1, 1 0 -> 0, 0 1 -> -1
def mergey(data):
    ret = []
    for i in range(0, len(data), 2):
        first = data[i]
        second = data[i+1]
        if first==0 and second == 0:
            ret.append(1)
        elif first == 1 and second == 0:
            ret.append(0)
        else:
            ret.append(-1)
    return ret

#setup data for x y and IDs for snippet and page
x_snippet_p, y_snippet_p, name_snippet = get_x_y(data_snippet)
x_page_p, y_page_p, name_page = get_x_y(data_page)

#add x and y in snippet with same IDs.
x_snippet_t = mergex(x_snippet_p)
y_snippet = mergey(y_snippet_p)

#add x and Y in page with same IDs.
x_page_t = mergex(x_page_p)
y_page = mergey(y_page_p)

#scale x of snippet and page to be standarized between 0 and 1.
sc = StandardScaler()
x_snippet = sc.fit_transform(x_snippet_t)
x_page = sc.fit_transform(x_page_t)

#constants got by linear regression for snippet and page
snippet = [-0.26627384, -0.01015289, -0.01414353, 0.00772591, 0.00567797, -0.00488698, -0.00141424, -0.00396811, -0.00702941, 0.00567797, 0.00114039]
page = [-0.26642613, -0.01038128, -0.01451397, 0.00244144, 0.005583, -0.00516817, -0.00126429, -0.00338472, 0.01146894, 0.005583, 0.00122292]

#with constants, X, y and ID, make list of [ID, TRUE/FALSE, TRUE/FALSE]
#which is in shape to be printed.
def generate_result(newB, testX, Y, names):
    result = []
    ran = 0.1
    for i in range(len(testX)):
        temp = []
        temp.append(names[2*i])
        val = 0
        for j in range(len(testX[i])):
            val += newB[j]*testX[i][j]
        if val > ran :
            temp.append("FALSE")
            temp.append("FALSE")
        elif val < -ran:
            temp.append("FALSE")
            temp.append("TRUE")
        else:
            temp.append("TRUE")
            temp.append("FALSE")
        result.append(temp)
    return result


#change everything to be in shape ready to print.
snif_result = generate_result(snippet, x_snippet, y_snippet, name_snippet)
page_result = generate_result(page, x_page, y_page, name_page)


#print snippet output
tsv_file = open("CSV372_HW5_snippet_output_20160632.tsv", 'w', newline = '')
write_tsv = csv.writer(tsv_file, delimiter="\t")
for i in snif_result:
    write_tsv.writerow([i[0], i[1], i[2]])
tsv_file.close()


#print page output
tsv_file = open("CSV372_HW5_page_output_20160632.tsv", 'w', newline = '')
write_tsv = csv.writer(tsv_file, delimiter="\t")
for i in page_result:
    write_tsv.writerow([i[0], i[1], i[2]])


tsv_file.close()



