##read it from
import numpy as np
import math
import json
from utils import generate_candidate_list, createNoisyChannel, naive_languange_model
vocabularies = {}

LEFT = 0
DOWN = 1
DIAG = 2

anslines = []
with open("ans.txt") as fp:

    for i in range(1000):
        ansline=fp.readline().split('\t')[1]
        anslines.append(ansline)

with open("mylm.json") as fp:
    vocabularies = json.loads(fp.read())

# with open("retuer.lm", 'r') as fp:
#     lines = fp.readlines()
#
#     index = 0
#
#     ##find the starting of 1-gram
#     divide_str = "\\1-grams:\n"
#     while lines[index] != divide_str:
#         index += 1
#
#     index += 1
#
#
#     ##finish util the ending of 2-gram
#     while lines[index] != "\n":
#         try:
#             (log_value, word) = lines[index].strip('\n').split('\t')[0:2]
#             vocabularies[word] = {
#                 "log_value": float(log_value),
#                 "candidates": {}
#             }
#         except:
#             print(index)
#         finally:
#             index += 1
#
#     index += 2
#
#     while lines[index] != '\n':
#         temp = lines[index]
#         (log_value, word_two_str) = lines[index].strip('\n').split('\t')[0:2]
#         word_two = word_two_str.split(" ")
#         vocabularies[word_two[0]]['candidates'][word_two[1]] = {
#             "probility": float(log_value)
#         }
#         index += 1

with open("vocab.txt") as fp:
    vocabs = fp.readlines()

    for vocab in vocabs:
        vocab = vocab.strip('\r\n')
        if vocabularies.get(vocab) is None:
            vocabularies[vocab] = {
                "log_value": -100,
                "candidates": {}
            }
        if vocabularies.get(vocab+"'") is None:
            vocabularies[vocab+"'"] = {
                "log_value": -100,
                "candidates": {}
            }
        if vocabularies.get(vocab+',') is None:
            vocabularies[vocab + ","] = {
                "log_value": -100,
                "candidates": {}
            }
        if vocabularies.get(vocab+'.') is None:
            vocabularies[vocab + "."] = {
                "log_value": -100,
                "candidates": {}
            }
        if vocabularies.get(vocab+"'s") is None:
            vocabularies[vocab + "'s"] = {
                "log_value": -100,
                "candidates": {}
            }



test_sentences = []

with open("testdata.txt", 'r') as fp:
    lines = fp.readlines()

    for (index, line) in enumerate(lines):
        (index_str, error_count_str, sentence_str) = (line.split('\t'))
        tokens = sentence_str.strip("\n").strip("\r").split(" ")

        test_sentences.append({
            'expected_error_count': int(error_count_str),
            'sentence': sentence_str,
            'tokens': tokens,
            'real_error_count': 0,
            "error_words_list": []
        })

def caculateNoisyChannel(current_word, candidate, noisy_channel):

    method = candidate[1]
    two_chars = candidate[2].lower()


    if method == "delete":

        count = noisy_channel['count_matrix'].get(two_chars)
        if count is None:
            count = 10000

        try:
            delete = noisy_channel['delete_matrix'][two_chars]
        except:
            delete = 1
        finally:
            if delete == 0:
                delete += 1

            return float(delete)/count

    if method == "substitute":

        count = noisy_channel['count_matrix'].get(two_chars[0])
        if count is None:
            count = 10000

        try:
            substitute = noisy_channel['substitute_matrix'][two_chars]
        except:
            substitute = 1
        finally:
            if substitute == 0:
                substitute += 1

            return float(substitute) / count

    if method == "switch":
        count = noisy_channel['count_matrix'].get(two_chars)
        if count is None:
            count = 10000

        try:
            switch = noisy_channel['switch_matrix'][two_chars]
        except:
            switch+=1
        finally:
            if switch == 0:
                switch += 1

            return float(switch) / count

    if method == "add":
        count = noisy_channel['count_matrix'].get(two_chars[0])
        if count is None:
            count = 10000
        try:
            add = noisy_channel['add_matrix'][two_chars]
        except:
            add += 1
        finally:
            if add == 0:
                add += 1

            return float(add) / count





def uniGram(vocabularies, index, sentence, candidate_list, noisy_channel):

    current_word = sentence['tokens'][index]
    if len(candidate_list) == 1:
        return candidate_list.pop()[0]


    max_value = -10000000
    max_word = ""
    for candidate in candidate_list:
        if isinstance(candidate, str):
            continue

        raw_noise_value = caculateNoisyChannel(current_word, candidate, noisy_channel)
        noise_channel = math.log(raw_noise_value)

        value = vocabularies[current_word]['log_value'] + noise_channel


        if value > max_value:
             max_word = candidate[0]
             max_value = vocabularies[candidate[0]]['log_value']
        return max_word


def biGram(vocabularies, index, sentence, candidate_list, noisy_channel):

    current_word = sentence['tokens'][index]
    if len(candidate_list) == 1:
        return candidate_list.pop()[0]

    max_value = -10000000
    max_word = ""


    ##the first has no preious word, use <s>
    if index == 0 or sentence['tokens'][index - 1] == "":
        previous_word = "<s>"
    else:
        previous_word = sentence['tokens'][index - 1]

    for candidate in candidate_list:

        if isinstance(candidate, str):
            continue

        condition_value = vocabularies[previous_word]['candidates'].get(current_word)

        # noisy_channel = math.log(caculateNoisyChannel(current_word, candidate, noisy_channel))

        noisy_channel = 0

        ##smooth
        if condition_value is None:
            value = vocabularies[candidate[0]]['log_value'] - 6 + noisy_channel
            if max_value < value:
                max_value = value
                max_word = candidate[0]

        else:
            value = vocabularies[candidate[0]]['log_value'] + condition_value['probility'] + noisy_channel
            if value > max_value:
                max_value = value
                max_word = candidate[0]

    return max_word


def CorrectSentence(sentence, vocabularies, fp, noise_channel):

    for (index, token) in enumerate(sentence['tokens']):
        if token != "" and vocabularies.get(token) is None:

            sentence['real_error_count'] += 1
            sentence['error_words_list'].append(token)

            candidate_list = set()
            candidate_list.add(token)
            candidate_list = generate_candidate_list(token, vocabularies, candidate_list, 1)

            if len(candidate_list) == 0:
                fp.write(str(index + 1) + '\t' + sentence['sentence'] + '\n')
                continue

            print("wrong word: {0}".format(token))
            print("candidate_list {0}".format(candidate_list))


            # proper_word = uniGram(vocabularies, index, sentence, candidate_list, noise_channel)


            proper_word = biGram(vocabularies, index, sentence, candidate_list, noise_channel)

            ## if it can not be found anyway,do not change sentences
            if proper_word is None:
                proper_word = token
                print("EMPTY!!!!!\n\n")


            print("proper_word {0}".format(proper_word))
            sentence['tokens'][index] = proper_word

    sentence['correct_sentence'] = ""


    for token in sentence['tokens']:
        sentence['correct_sentence'] += (token+" ")


    print("raw_sentence    : {0}".format(sentence['sentence']))

    sentence['correct_sentence'] = sentence['correct_sentence'][0:-1]

    print("correct_sentence: {0}".format(sentence['correct_sentence']))

    fp.write(str(index+1)+'\t'+sentence['correct_sentence']+'\n')





with open("result.txt", 'w') as fp:

    noisy_channel = createNoisyChannel()

    count = 0

    for (index, sentence) in enumerate(test_sentences):

        CorrectSentence(sentence, vocabularies, fp, noisy_channel)

        ansline = anslines[index].strip('\r\n')
        print("answer_sentence : {0}".format(ansline))
        if (sentence['correct_sentence'] == ansline):
            print("bingo")
            count += 1
        print("\n\n")

    print(count)
# with open("none", 'w') as fp:
#     CorrectSentence(test_sentences[998], vocabularies, fp, noise_channel)























