import numpy as np
import math
import json
from utils import generate_candidate_list, createNoisyChannel
from test import loadAnswer, CorrectSentence, loadStandardLanguageModel, loadYourLanguangeModel, loadTestData


class SpellCorrrection:

    def __init__(self,result_filename, answer_filename, lm_filename, test_filename):
        self.fp = open(result_filename, 'w')
        self.anslines = loadAnswer(answer_filename)
        self.vocabularies = loadStandardLanguageModel(lm_filename)
        self.test_sentences = loadTestData(test_filename)
        self.noisy_channel = createNoisyChannel()
        self.count = 0

    def __del__(self):
        self.fp.close()

    def start(self):

        for (index, sentence) in enumerate(self.test_sentences):

            CorrectSentence(sentence, self.vocabularies, self.fp, self.noisy_channel)

            ansline = self.anslines[index].strip('\r\n')
            print("answer_sentence : {0}".format(ansline))
            if (sentence['correct_sentence'] == ansline):
                print("bingo")
                self.count += 1
            print("\n\n")

        print(self.count)





if __name__ == '__main__':

    spell_correction = SpellCorrrection('result.txt','ans.txt','retuer.lm', 'testdata.txt')
    spell_correction.start()





