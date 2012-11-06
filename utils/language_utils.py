from utils.load_utils import load_ngrams, load_words, load_initial_ngrams, load_anagrams, load_synonyms
import re
from nltk.corpus import wordnet as wn
from cryptic_utils import additional_synonyms


NGRAMS = load_ngrams()
INITIAL_NGRAMS = load_initial_ngrams()
WORDS = load_words()
ANAGRAMS = load_anagrams()
SYNONYMS = load_synonyms()
for s in additional_synonyms:
    SYNONYMS[s].update(additional_synonyms[s])


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


def cached_anagrams(x, length):
    x = x.lower().replace(' ', '')
    if len(x) > length:
        return ['']
    if x in ANAGRAMS:
        return filter(lambda y: y != x, ANAGRAMS[x])
    else:
        return filter(lambda y: y != x, anagrams(x))


def cached_synonyms(x, length):
    x = x.lower()
    syns = [s for s in SYNONYMS[x.replace(' ', '_')] if len(s) <= length]
    if len(syns) == 0:
        syns = [x]
    return list(syns)


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


def substring_words(sentence, length):
    sentence = re.sub(' ', '', sentence).lower()
    for i in range(len(sentence) - length + 1):
        s = sentence[i:i + length]
        if s in WORDS:
            yield s


def all_legal_substrings(word, length):
    word = word.lower()
    subs = []
    for l in range(1, min(len(word) - 1, length) + 1):
        subs.extend(legal_substrings(word, l))
        subs.extend(substring_words(word, l))
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


def all_insertions(word1, word2, length):
    """
    Try inserting word1 into word2 and vice-versa
    """
    if word1 == '' or word2 == '':
        yield word1 + word2
    for w0, w1 in [(word1, word2), (word2, word1)]:
        for j in range(len(w1)):
            yield w1[:j] + w0 + w1[j:]


def matches_pattern(word, pattern):
    """
    Pattern is a very basic regex, which must have a letter-for-letter mapping with the target string. For example, '.s...a.' is good, but '.s.*a.' will not work.
    """
    if pattern == '':
        return True
    else:
        return bool(re.match(pattern[:len(word)], word))

