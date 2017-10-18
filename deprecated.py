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

def languangeModel():
    '''
    The standard languange model, using FSM to seperate sentences, not finished yet
    :return:
    '''
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


def edit_distance(word1, word2, max_distance):
    '''
    The time-comsuming way to generate edit distance
    :param word1:
    :param word2:
    :param max_distance:
    :return:
    '''
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







    return ([],distance[i][j])

    routes = []
    trace_back_i = len2 - 1
    trace_back_j = len1 - 1

    while trace_back_i != 1 or trace_back_j != 1:
        if direction[trace_back_i][trace_back_j] == LEFT:
            routes.append({
                "method": "deletion",
                "characters": [word1[trace_back_j-1], word1[trace_back_j]]
            })
            trace_back_j -= 1

        if direction[trace_back_i][trace_back_j] == DOWN:
            routes.append({
                "method": "insertion",
                "characters": [word1[trace_back_j], word2[trace_back_i]]
            })
            trace_back_i -= 1

        if direction[trace_back_i][trace_back_j] == DIAG_SWAP:
            routes.append({
                "method": "switch",
                "characters": [word1[trace_back_j], word2[trace_back_i]]
            })
            trace_back_i -= 1
            trace_back_j -= 1

        if direction[trace_back_i][trace_back_j] == DIAG_NON_SWAP:
            trace_back_i -= 1
            trace_back_j -= 1



    return (routes, distance[len2-1][len1-1])