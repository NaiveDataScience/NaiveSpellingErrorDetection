import json
import nltk

def naiveLanguangeModel():
    '''
    The gross implementation of languange model, but seems to work well
    :return:
    '''
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