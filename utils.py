import copy
import numpy as np
import nltk
import math
import json

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
                try:
                    if j == word_len:
                        temp = insert_word[j-1]
                    else:
                        temp = insert_word[j]
                except:
                    pass

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

    ##If not none, return
    if len(filter_list) != 0:
        return filter_list
    #else continue deeper search recursively
    else:
        candidate_list = set(map(lambda candidate: candidate[0], candidate_list))
        return generate_candidate_list(current_word, vocabularies, candidate_list, deepth+1)



if __name__ == '__main__':
    createNoisyChannel()