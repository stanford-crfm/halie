import csv
import numpy as np
import collections


def read_human_eval(path):
    human_eval = collections.defaultdict(list)
    worker_ids = set()
    with open(path, 'r') as data:
        for row in csv.DictReader(data):
            sentence = row['Input.metaphorical_sentence']
            apt = 1 if row['Answer.aptness.apt'] == 'true' else 0
            specific = 1 if row['Answer.specificity.specific'] == 'true' else 0
            imageable = 1 if row['Answer.imaginable.imaginable'] == 'true' else 0

            human_eval[sentence].append((apt, imageable, specific))
            worker_ids.add(row['WorkerId'])

    print('Number of human annotators:', len(worker_ids))
    return human_eval


def get_human_eval(sentence):
    if sentence in human_eval:
        annotations = human_eval[sentence]

        apt, specific, imageable = [], [], []
        for (a, s, i) in annotations:
            apt.append(a)
            specific.append(s)
            imageable.append(i)
        return (np.mean(apt), np.mean(specific), np.mean(imageable))
    else:
        return (None, None, None)


path = '/Users/minalee/Research/writingwithai/public/assets/raw/metaphor/eval/third_party_results.csv'
human_eval = read_human_eval(path)
