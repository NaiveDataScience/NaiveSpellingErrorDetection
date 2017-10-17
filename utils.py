import copy
import numpy as np
LEFT = 0
DOWN = 1
DIAG = 2
DIAG_NON_SWAP =3
DIAG_SWAP = 4


def languange_model():

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




def generate_candidate_list(word, vocabularies, degree, candidate_list):

    copy_candidate_list = copy.deepcopy(candidate_list)

    for word in copy_candidate_list:
        word_len = len(word)

        for i in range(0, 26):
            ##insertion,
            for j in range(0, word_len+1):

                insert_word = map(lambda x: x, word)
                insert_word.insert(j, chr(ord('a')+i))

                insert_word = reduce(lambda x, y: x + y, insert_word, "")
                candidate_list.add(insert_word)

            ##replace
            for j in range(0, word_len):
                replace_word = map(lambda x: x, word)
                replace_word[j] = chr(ord('a')+i)

                replace_word = reduce(lambda x, y:x+y, replace_word, "")
                candidate_list.add(replace_word)

        ##deletion
        for i in range(0, word_len):
            delete_word = map(lambda x: x, word)
            del delete_word[i]
            delete_word = reduce(lambda x, y: x + y, delete_word, "")
            candidate_list.add(delete_word)

        ##switch
        for i in range(0, word_len-1):
            switch_word = map(lambda x: x, word)
            temp = switch_word[i]
            switch_word[i] = switch_word[i+1]
            switch_word[i+1] = temp

            switch_word = reduce(lambda x, y: x+y, switch_word, "")
            candidate_list.add(switch_word)

    if degree == 1:
        ## filter out the true word
        filter_list = set(filter(lambda item: vocabularies.get(item) is not None, candidate_list))
        return filter_list
    else:
        degree -= 1
        return generate_candidate_list(word, vocabularies, degree, candidate_list)



if __name__ == '__main__':
    (routes, distance) =edit_distance('tionst', 'tionist', 2)
    print(routes)
    print(distance)