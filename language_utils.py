import cPickle as pickle
from load_utils import load_ngrams
import re
from nltk.corpus import wordnet as wn

NGRAMS = load_ngrams()


def anagrams(letters, active_set = ['']):
    letters = re.sub(r'\ ', '', str(letters))
    if len(active_set[0]) == len(letters):
        return active_set
    else:
        new_active_set = []
        for w in active_set:
            for l in set(remaining_letters(letters, w)):
                candidate = w + l
                if candidate in NGRAMS[len(candidate)]:
                    new_active_set.append(candidate)
        if len(new_active_set) == 0:
            return []
        else:
            return anagrams(letters, new_active_set)


class AnagramDict(dict):
    def __missing__(self, key):
        self[key] = anagrams(key)
        return self[key]


def remaining_letters(letters, w):
    for c in set(letters):
        if letters.count(c) > w.count(c):
            yield c

def synonyms(word):
    word = re.sub(r'\ ', '_', word)
    answers = set([])
    for synset in wn.synsets(word):
        all_synsets = synset.similar_tos()
        all_synsets.append(synset)
        for similar_synset in all_synsets:
            for lemma in similar_synset.lemmas:
                if lemma.name != word:
                    answers.add(lemma.name)
    return answers


def all_legal_substrings(word):
    subs = []
    for l in range(1, len(word) + 1):
        subs.extend(legal_substrings(word, l))
    return subs


def legal_substrings(word, length):
    yield word[:length]
    yield word[-length:]
    if len(word) % 2 == 0 and length % 2 == 0:
        yield word[:length//2] + word[-length//2:]
        yield word[len(word)//2-length//2:len(word)//2+length//2]
    elif len(word) % 2 == 1 and length % 2 == 1:
        yield word[len(word)//2-length//2:len(word)//2+length//2+1]


def semantic_similarity(word1, word2):
    word1.replace(' ', '_')
    word2.replace(' ', '_')
    max_p = 0
    for s1 in wn.synsets(word1):
        for st1 in [s1] + s1.similar_tos():
            for s2 in wn.synsets(word2):
                for st2 in [s2] + s2.similar_tos():
                    p = wn.wup_similarity(st1, st2)
                    if p > max_p:
                        max_p = p
    return max_p


def all_insertions(word1, word2):
    """
    Try inserting word1 into word2 and vice-versa
    """
    for w0, w1 in [(word1, word2), (word2, word1)]:
        for j in range(1, len(w1)):
            yield w1[:j] + w0 + w1[j:]
