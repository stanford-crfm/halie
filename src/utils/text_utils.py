import string


def count_num_words(sentence):
    return len(sentence.split())


def get_levenshtein_distance(s1, s2):
    assert not isinstance(s1, str)
    assert not isinstance(s2, str)

    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def normalize_text(sentence):
    sentence = sentence.lower().replace('\n', ' ').strip()
    return sentence.translate(str.maketrans('', '', string.punctuation))
