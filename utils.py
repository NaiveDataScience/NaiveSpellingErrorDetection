import copy
import numpy as np
import nltk
import math
import json
LEFT = 0
DOWN = 1
DIAG = 2
DIAG_NON_SWAP =3
DIAG_SWAP = 4

def languange_model():
    with open("retuer.txt") as fp:
        lines = fp.readlines()

    model = []
    state = ""
    title = []
    sentence = []
    for line in lines:
        line = line.strip("\n")
        if state == " " and line[0] != " ":
            state = "magazine"
            continue
        if state == "magazine" and line[2] != " ":
            state = "title"
            title = line.split(" ")
        if state == "title" and line[2] == " " and line[7] != " ":
            state = "sentence"
            sentence = 4

        if state == "title" and line[1] != " " and True:
            pass

def naive_languange_model():
    with open("retuer.txt") as fp:
        lines = fp.readlines()

    sentences = []
    for line in lines:
        sentence = nltk.word_tokenize(line)
        sentences.extend(sentence)

    vocabularies = {}

    for (index, word) in enumerate(sentences):
        ##last one has no candidate
        if index == len(sentences)-1:
            break

        if vocabularies.get(word) is None:
            vocabularies[word] = {
                "word_count": 0,
                "log_value": 0,
                "candidates": {},
                "candidate_number": 0
            }
        vocabularies[word]["word_count"] += 1

        next_word = sentences[index+1]
        if vocabularies[word]["candidates"].get(next_word) is None:
            vocabularies[word]["candidates"][next_word] = {
                "count": 1,
                "probility": -1
            }
        else:
            vocabularies[word]["candidates"][next_word]["count"] += 1

        vocabularies[word]["candidate_number"] += 1

    vocab_lens = len(vocabularies)

    ##Take the beginning <s> into consideration
    begin = {
        "candidates": {}
    }

    for (key, vocabulary) in vocabularies.items():
        candidate_number = vocabularies[key]["candidate_number"]
        try:
            vocabularies[key]['log_value'] = math.log(float(vocabularies[key]['word_count'])/vocab_lens)
        except:
            print("gg")
            print(vocabularies[key]['word_count'])

        try:
            for (key2, value) in vocabularies[key]["candidates"].items():
                vocabularies[key]["candidates"][key2]["probility"] = math.log(float(value["count"])/candidate_number)
        except:
            print(vocabularies[key]["candidates"][key2]["probility"])
            print("LLL")

        begin["candidates"][key] = {
            "probility": vocabularies[key]['log_value']
        }

    vocabularies["<s>"] = begin

    with open("vocab.txt") as fp:
        vocabs = fp.readlines()

        for vocab in vocabs:
            vocab = vocab.strip('\r\n')
            if vocabularies.get(vocab) is None:
                vocabularies[vocab] = {
                    "log_value": -100,
                    "candidates": {}
                }
            if vocabularies.get(vocab + "'") is None:
                vocabularies[vocab + "'"] = {
                    "log_value": -100,
                    "candidates": {}
                }
            if vocabularies.get(vocab + ',') is None:
                vocabularies[vocab + ","] = {
                    "log_value": -100,
                    "candidates": {}
                }
            if vocabularies.get(vocab + '.') is None:
                vocabularies[vocab + "."] = {
                    "log_value": -100,
                    "candidates": {}
                }
            if vocabularies.get(vocab + "'s") is None:
                vocabularies[vocab + "'s"] = {
                    "log_value": -100,
                    "candidates": {}
                }


    with open("mylm.json", 'w') as fp:
        fp.write(json.dumps(vocabularies))




def edit_distance(word1, word2, max_distance):

    word1 = "#" + word1
    word2 = "#" + word2

    len1 = len(word1)
    len2 = len(word2)


    distance = np.zeros(len1*len2).reshape(len2, len1)
    direction = np.zeros(len1*len2).reshape(len2, len1)

    ##switch
    if len1 == len2:
        cursor = 0

        while cursor < len1 and word1[cursor] == word2[cursor]:
            cursor += 1

        if cursor == len1:
            return ([], 0)

        if cursor+1 < len1 and word1[cursor] == word2[cursor+1] and word1[cursor+1] == word2[cursor]:
            marker = cursor
            cursor += 1

            while cursor < len1 and word1[cursor] != word2[cursor]:
                cursor += 1

            if cursor == len1:
                a = word1[marker]
                b = word2[marker]
                return([{
                        "method": "switch",
                        "characters": [a, b]
                            }], 1)


    ##Not switch
    for i in range(0, len1):
        distance[0][i] = i

    for i in range(0, len2):
        distance[i][0] = i

    routes = []
    for i in range(1, len2):
        for j in range(1, len1):
            ##check whether diagonal is a real swap
            substitute = False
            method = [0, 0, 0]
            method[LEFT] = distance[i][j-1] + 1
            method[DOWN] = distance[i-1][j] + 1

            if word1[j] == word2[i]:
                method[DIAG] = distance[i-1][j-1] + 0
            else:
                substitute = True
                method[DIAG] = distance[i-1][j-1] + 1

            distance[i][j] = method[DIAG]


            if substitute is True:
                direction[i][j] = DIAG_SWAP
            else:
                direction[i][j] = DIAG_NON_SWAP

            if method[LEFT] < distance[i][j]:
                distance[i][j] = method[LEFT]
                direction[i][j] = LEFT

            if method[DOWN] < distance[i][j]:
                distance[i][j] = method[DOWN]
                direction[i][j] = DOWN

    trace_back_i = len2-1
    trace_back_j = len1-1

    routes = []



    return ([],distance[i][j])


    # while trace_back_i != 1 or trace_back_j != 1:
    #     if direction[trace_back_i][trace_back_j] == LEFT:
    #         routes.append({
    #             "method": "deletion",
    #             "characters": [word1[trace_back_j-1], word1[trace_back_j]]
    #         })
    #         trace_back_j -= 1
    #
    #     if direction[trace_back_i][trace_back_j] == DOWN:
    #         routes.append({
    #             "method": "insertion",
    #             "characters": [word1[trace_back_j], word2[trace_back_i]]
    #         })
    #         trace_back_i -= 1
    #
    #     if direction[trace_back_i][trace_back_j] == DIAG_SWAP:
    #         routes.append({
    #             "method": "switch",
    #             "characters": [word1[trace_back_j], word2[trace_back_i]]
    #         })
    #         trace_back_i -= 1
    #         trace_back_j -= 1
    #
    #     if direction[trace_back_i][trace_back_j] == DIAG_NON_SWAP:
    #         trace_back_i -= 1
    #         trace_back_j -= 1
    #
    #
    #
    # return (routes, distance[len2-1][len1-1])

def createNoisyChannel():

    noisy_channel = {}

    with open("revconfusion.data") as fp:
        rev_matrix = eval(fp.read())
        noisy_channel['switch_matrix'] = rev_matrix

    with open("subconfusion.data") as fp:
        sub_matrix = eval(fp.read())
        noisy_channel['substitute_matrix'] = sub_matrix

    with open("delconfusion.data") as fp:
        del_confusion = eval(fp.read())
        noisy_channel['delete_matrix'] = del_confusion

    with open("addconfusion.data") as fp:
        add_matrix = eval(fp.read())
        noisy_channel['add_matrix'] = add_matrix

    #count
    count_matrix = {}
    for (key, matrix) in noisy_channel.items():
        for (key2, value) in matrix.items():

            if count_matrix.get(key2) is None:
                count_matrix[key2] = 0

            count_matrix[key2] += value

            if count_matrix.get(key2[0]) is None:
                count_matrix[key2[0]] = 0

            count_matrix[key2[0]] += value

    noisy_channel['count_matrix'] = count_matrix

    return noisy_channel


def generate_candidate_list(current_word, vocabularies, candidate_list, deepth):

    if deepth == 3:
        return candidate_list

    copy_candidate_list = copy.deepcopy(candidate_list)

    for word in copy_candidate_list:
        word_len = len(word)

        for i in range(0, 26):
            ##insertion,
            for j in range(0, word_len+1):

                insert_word = map(lambda x: x, word)

                ##save the word
                if j == word_len:
                    temp = insert_word[j-1]
                else:
                    temp = insert_word[j]

                insert_word.insert(j, chr(ord('a')+i))

                insert_word = reduce(lambda x, y: x + y, insert_word, "")

                ##this is reverse to thesis
                candidate_list.add((insert_word, 'delete', temp+chr(ord('a')+i)))

            ##replace
            for j in range(0, word_len):
                replace_word = map(lambda x: x, word)

                ##save the word
                temp = replace_word[j]
                replace_word[j] = chr(ord('a')+i)

                replace_word = reduce(lambda x, y:x+y, replace_word, "")
                candidate_list.add((replace_word, 'substitute', temp+replace_word[j]))

        ##deletion
        for i in range(0, word_len):
            delete_word = map(lambda x: x, word)
            if i > 1:
                temp1 = delete_word[i-1]
            else:
                temp1 = delete_word[i]

            temp2 = delete_word[i]
            del delete_word[i]
            delete_word = reduce(lambda x, y: x + y, delete_word, "")
            candidate_list.add((delete_word, 'add', temp1+temp2))

        ##switch
        for i in range(0, word_len-1):
            switch_word = map(lambda x: x, word)
            temp = switch_word[i]
            switch_word[i] = switch_word[i+1]
            switch_word[i+1] = temp

            switch_word = reduce(lambda x, y: x+y, switch_word, "")
            candidate_list.add((switch_word, 'switch', switch_word[i]+switch_word[i+1]))

    ## filter out the true word
    if current_word in candidate_list:
        candidate_list.remove(current_word)

    filter_list = set(filter(lambda item: isinstance(item, tuple) and vocabularies.get(item[0]) is not None, candidate_list))

    ##If not none, return ,
    if len(filter_list) != 0:
        return filter_list
    #else continue deeper search
    else:
        candidate_list = set(map(lambda candidate: candidate[0], candidate_list))
        return generate_candidate_list(current_word, vocabularies, candidate_list, deepth+1)



if __name__ == '__main__':
    naive_languange_model()