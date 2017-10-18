##read it from
import numpy as np
import math
import json
from utils import generate_candidate_list, createNoisyChannel
vocabularies = {}

LEFT = 0
DOWN = 1
DIAG = 2

BIGRAM_BIAS = -6
BIGRAM_THETA = 0.8

anslines = []
def loadAnswer(filename):
    '''
    Load the right answer, which will be convinient to compare with your result
    :param filename
    :return: anslines
    '''
    with open("ans.txt") as fp:
        anslines = []
        for i in range(1000):
            ansline=fp.readline().split('\t')[1]
            anslines.append(ansline)

    return anslines

def loadYourLanguangeModel(filename):
    '''
    Load your own language model
    :param filename
    :return: your own model
    '''
    with open("mylm.json") as fp:
        vocabularies = json.loads(fp.read())

    return vocabularies

def loadStandardLanguageModel(filename):
    '''
    Load the third part languange model
    :param filename:
    :return: model
    '''

    vocabularies = {}

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
                    "candidates": {}
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
            vocabularies[word_two[0]]['candidates'][word_two[1]] = {
                "probility": float(log_value)
            }
            index += 1

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

    return vocabularies


def loadTestData(filename):
    '''
    load the test data
    :param filename: test data's filename
    :return: test_data_sentence
    '''
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
                'noneword_error_count': 0,
                "error_words_list": []
            })

    return test_sentences

def caculateNoisyChannel(current_word, candidate, noisy_channel):
    '''
    Caculate noisy channel value with confusing matirx
    :param current_word: current word
    :param candidate: the candidate word
    :param noisy_channel: a model about confusing matirx
    :return: noisy value
    '''
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
    '''
    Choose the most proper word from candidate list in unigram mode
    :param vocabularies: vocabularies
    :param index: the index of the word in sentence
    :param sentence: the current sentence
    :param candidate_list: the list of candidates, need to be picked up
    :param noisy_channel: the nosiy channel model
    :return: the most proper word
    '''
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
    '''
    Choose the most proper word from candidate list in bigram mode
    :param vocabularies: vocabularies
    :param index: the index of the word in sentence
    :param sentence: the current sentence
    :param candidate_list: the list of candidates, need to be picked up
    :param noisy_channel: the nosiy channel model
    :return: the most proper word
    '''
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

        condition_value = getBigramValue(vocabularies, previous_word, current_word)


        # noisy_channel = math.log(caculateNoisyChannel(current_word, candidate, noisy_channel))

        noisy_channel = 0

        value = vocabularies[candidate[0]]['log_value'] + BIGRAM_THETA*condition_value + noisy_channel
        if value > max_value:
            max_value = value
            max_word = candidate[0]

    return max_word

def getBigramValue(vocabularies, previous_word, current_word):
    '''
    caculate bigram error, should implement smoothing....
    :param vocabularies: vocabularies
    :param previous_word: pre
    :param current_word: current
    :return:
    '''
    condition_value = vocabularies[previous_word]['candidates'].get(current_word)

    ##smoothing
    if condition_value is None:
        return BIGRAM_BIAS

    return condition_value['probility']

def correctNoneWordError(sentence, vocabularies, fp, noise_channel):
    '''

    :param sentence: sentence need to correct
    :param vocabularies: vocabularies
    :param fp: file descriptor
    :param noise_channel: noise_channel
    :return:
    '''
    for (index, token) in enumerate(sentence['tokens']):

        if token != "" and vocabularies.get(token) is None:

            sentence['noneword_error_count'] += 1
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

def correctRealWordError(sentence, vocabularies, fp, noise_channel, realword_error_count):
    '''

    :param sentence: sentence which has correct the none word error
    :param vocabularies: vocabularies
    :param fp: fp
    :param noise_channel: noise_channel
    :param realword_error_count: the number of error need to be correct
    :return: None
    '''

    ##We only discuss the naive situation
    if realword_error_count != 1:
        return

    final_max_value = -100000
    final_max_word = ""

    for (index, token) in enumerate(sentence['tokens']):
        if token != "" and vocabularies.get(token) is None:
            candidate_list = set()
            candidate_list.add(token)

            candidate_list = generate_candidate_list(token, vocabularies, candidate_list, 1)

            max_word = ""
            max_value = -100000
            for candidate in candidate_list:

                if index == 0:
                    pre = "<s>"
                    next = sentence['tokens'][index + 1]
                elif index == len(sentence['tokens'])-1:
                    ##we do not handle </s>
                    continue
                else:
                    pre = sentence['tokens'][index-1]
                    next = sentence['tokens'][index+1]

                ##exclude the case of ""
                if pre == "" or next == "":
                    continue

                pre_value = getBigramValue(vocabularies, pre, candidate[0])
                post_value = getBigramValue(vocabularies, candidate[0], next)
                value = pre_value + post_value

                if value > max_value:
                    max_value = value
                    max_word = candidate[0]

            if max_value > final_max_value:
                final_max_value = max_value
                final_max_word = max_word

    print("real_word error {0}".format(final_max_word))
    sentence['tokens'][index] = final_max_word


def CorrectSentence(sentence, vocabularies, fp, noise_channel):
    '''
    Correct the sentence and write it to your answer sheet
    :param sentence: the original sentence
    :param vocabularies: vocabularies
    :param fp: file descriptor, used to write to "result.txt"
    :param noise_channel: noise_channel
    :return: None
    '''

    correctNoneWordError(sentence, vocabularies, fp, noise_channel)


    ##When your finished the non-word error, pay attention to the real word error
    if sentence['noneword_error_count'] < sentence['expected_error_count']:
        realword_error_count = sentence['expected_error_count'] - sentence['noneword_error_count']
        print("noneword_error {0}, expected_error {1}".format(sentence['noneword_error_count'], sentence['expected_error_count']))
        correctRealWordError(sentence, vocabularies, fp, noise_channel, realword_error_count)


    sentence['correct_sentence'] = ""


    for token in sentence['tokens']:
        sentence['correct_sentence'] += (token+" ")


    print("raw_sentence    : {0}".format(sentence['sentence']))

    sentence['correct_sentence'] = sentence['correct_sentence'][0:-1]

    print("correct_sentence: {0}".format(sentence['correct_sentence']))

    fp.write(str(1)+'\t'+sentence['correct_sentence']+'\n')



























