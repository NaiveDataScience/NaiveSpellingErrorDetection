##read it from
import numpy as np
from utils import generate_candidate_list
vocabularies = {}

LEFT = 0
DOWN = 1
DIAG = 2

anslines = []
with open("ans.txt") as fp:

    for i in range(1000):
        ansline=fp.readline().split('\t')[1]
        anslines.append(ansline)

with open("retuer.lm", 'r') as fp:
    lines = fp.readlines()

    index = 0

    ##find the starting of 1-gram
    divide_str = "\\1-grams:\n"
    while lines[index] != divide_str:
        index += 1

    index += 1


    ##finish util the ending of 2-gram
    while lines[index] != "\n":
        try:
            (log_value, word) = lines[index].strip('\n').split('\t')[0:2]
            vocabularies[word] = {
                "log_value": float(log_value),
                "margov_chain": {}
            }
        except:
            print(index)
        finally:
            index += 1

    index += 2

    while lines[index] != '\n':
        temp = lines[index]
        (log_value, word_two_str) = lines[index].strip('\n').split('\t')[0:2]
        word_two = word_two_str.split(" ")
        vocabularies[word_two[0]]['margov_chain'][word_two[1]] = float(log_value)
        index += 1

with open("vocab.txt") as fp:
    vocabs = fp.readlines()

    for vocab in vocabs:
        vocab = vocab.strip('\r\n')
        if vocabularies.get(vocab) is None:
            vocabularies[vocab] = {
                "log_value": -100,
                "margov_chain": {}
            }
        if vocabularies.get(vocab+"'") is None:
            vocabularies[vocab+"'"] = {
                "log_value": -100,
                "margov_chain": {}
            }
        if vocabularies.get(vocab+',') is None:
            vocabularies[vocab + ","] = {
                "log_value": -100,
                "margov_chain": {}
            }
        if vocabularies.get(vocab+'.') is None:
            vocabularies[vocab + "."] = {
                "log_value": -100,
                "margov_chain": {}
            }
        if vocabularies.get(vocab+"'s") is None:
            vocabularies[vocab + "'s"] = {
                "log_value": -100,
                "margov_chain": {}
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




def chooseViaUnigram(vocabularies, index, sentence, candidate_list):

    if len(candidate_list) == 1:
        return candidate_list.pop()


    max_value = -10000000
    max_word = ""

    current_word = sentence['tokens'][index]


    ##the first has no preious word, use <s>
    if index == 0 or sentence['tokens'][index - 1]=="":
        previous_word = "<s>"
    else:
        previous_word = sentence['tokens'][index - 1]

    for word in candidate_list:
        # if vocabularies[word]['log_value'] > max_value:
        #     max_word = word
        #     max_value = vocabularies[word]['log_value']
        condition_value = vocabularies[previous_word]['margov_chain'].get(word)

        ##smooth
        if condition_value is None:
            value = vocabularies[word]['log_value']-100000
            if max_value < value:
                max_value = value
                max_word = word

        else:
            value = vocabularies[word]['log_value']+condition_value
            if value > max_value:
                max_value = value
                max_word = word

    return max_word


def CorrectSentence(sentence, vocabularies, fp):

    for (index, token) in enumerate(sentence['tokens']):
        if token != "" and vocabularies.get(token) is None:

            sentence['real_error_count'] += 1
            sentence['error_words_list'].append(token)

            candidate_list = set()
            candidate_list.add(token)
            candidate_list = generate_candidate_list(token, vocabularies, 1, candidate_list)

            print("wrong word: {0}".format(token))
            print("candidate_list {0}".format(candidate_list))
            proper_word = chooseViaUnigram(vocabularies, index, sentence, candidate_list)
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
    count = 0
    for (index, sentence) in enumerate(test_sentences):

        CorrectSentence(sentence, vocabularies, fp)
        ansline = anslines[index].strip('\r\n')
        print("answer_sentence : {0}".format(ansline))
        if (sentence['correct_sentence'] == ansline):
            print("bingo")
            count += 1
        print("\n\n")




    print(count)
# with open("none", 'w') as fp:
#     CorrectSentence(test_sentences[998], vocabularies, fp)























