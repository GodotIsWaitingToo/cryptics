from __future__ import division
from load_utils import load_words, load_initial_ngrams, load_anagrams, load_synonyms
from language_utils import all_legal_substrings, semantic_similarity, all_insertions, anagrams
from search import tree_search
import re

WORDS = load_words()
INITIAL_NGRAMS = load_initial_ngrams()
ANAGRAMS = load_anagrams()
SYNONYMS = load_synonyms()
SYNONYMS['siblings'].add('sis')

def cached_anagrams(x, length):
    if len(x) > length:
        return ['']
    if x in ANAGRAMS:
        return ANAGRAMS[x]
    else:
        return anagrams(x)

THRESHOLD = 0.5

all_phrases = [
               ['attractive', 'female', 'engraving', 8, ''],
               ['join', 'trio of', 'astronomers', 'in', 'marsh', 6, 'f.....'],
               ['host', 'played', 'in the', 'pool', 'around', 'four', 'finally', (5), 's....'],
               ['spin', 'broken', 'shingle', 7, 'e......'],
               ['initially', 'babies', 'are', 'naked', 4, ''],
               ['tenor', 'and', 'alto', 'upset', 'count', 5, ''],
               ['sat', 'up', 'interrupting', 'siblings', 'balance', 6, ''],
               ['ach cole', 'wrecked', 'something in the ear', 7, ''],
               ['Bottomless', 'sea', 'stormy', 'sea', 'waters', 'surface', 'rises and falls', 7, '']
               ]


FUNCTIONS = {'ana': cached_anagrams, 'sub': all_legal_substrings, 'ins': all_insertions, 'rev': lambda x, l: [''.join(reversed(x))]}

KINDS = ['ana_r', 'ana_l', 'sub_r', 'sub_l', 'ins', 'rev_l', 'rev_l', 'lit', 'd', 'syn', 'first', 'null']


def valid_kinds(kinds):
    if (kinds[0] == 'd') == (kinds[-1] == 'd'):
        return False
    if any(k == 'd' for k in kinds[1:-1]):
        return False
    if ('_r' in kinds[-1] or kinds[-1] == 'ins'):
        return False
    if not valid_intermediate(kinds):
        return False
    return True


def valid_intermediate(kinds):
    if len(kinds) < 2:
        return True
    if ('_l' in kinds[0] or kinds[0] == 'ins'):
        return False
    if kinds[0] == 'd':
        if '_l' in kinds[1] or kinds[1] == 'ins':
            return False
    if any('_r' in kinds[i] and ('_l' in kinds[i + 1] or kinds[i + 1] == 'ins') for i in range(len(kinds) - 1)):
        return False
    if any(kinds[i] == 'ins' and '_r' in kinds[i + 1] for i in range(len(kinds) - 1)):
        return False
    if kinds[-1] == 'd':
        if '_r' in kinds[-2] or kinds[-2] == 'ins':
            return False
    if kinds.count('ana_l') + kinds.count('ana_r') > 1:
        return False
    if any('_r' in kinds[i] and kinds[i + 1] != 'lit' for i in range(len(kinds) - 1)):
        return False
    if any(kinds[i] != 'lit' and '_l' in kinds[i + 1] for i in range(len(kinds) - 1)):
        return False
    if any('_r' in kinds[i] and '_l' in kinds[i + 2] for i in range(len(kinds) - 2)):
        return False
    if any(('_r' in kinds[i] and kinds[i + 1] == 'null') or ('_l' in kinds[i + 1] and kinds[i] == 'null') for i in range(len(kinds) - 1)):
        return False
    return True


def generate_structured_clues(phrases, length, pattern):
    potential_kinds = tree_search([], [KINDS] * (len(phrases)),
                       combination_func=lambda s, w: s + [w],
                       member_test=valid_intermediate)
    for kinds in potential_kinds:
        if valid_kinds(kinds):
            yield zip(phrases, kinds) + [length, pattern]


def matches_pattern(word, pattern):
    """
    Pattern is a very basic regex, which must have a letter-for-letter mapping with the target string. For example, '.s...a.' is good, but '.s.*a.' will not work.
    """
    if pattern == '':
        return True
    else:
        return bool(re.match(pattern[:len(word)], word))


def solve_structured_clue(clue):
    pattern = clue.pop()
    length = clue.pop()
    definition, d = clue.pop([x[1] for x in clue].index('d'))
    groups_to_skip = set([])
    answer_subparts = [[] for x in clue]
    while any(s == [] for index, s in enumerate(answer_subparts) if index not in groups_to_skip):
        for i, group in enumerate(clue):
            if answer_subparts[i] != []:
                continue
            phrase, kind = group[:2]
            if kind[:3] in FUNCTIONS:
                if kind[:3] == 'ins':
                    arg_offsets = [-1, 1]
                    if i > 1 and '_r' in clue[i - 2][1]:
                        arg_offsets[0] = -2
                    if i < len(clue) - 2 and '_l' in clue[i + 2][1]:
                        arg_offsets[1] = 2
                    func = kind
                else:
                    func, direction = kind.split('_')
                    if direction == 'l':
                        arg_offsets = [-1]
                    else:
                        arg_offsets = [1]
                arg_indices = [i + x for x in arg_offsets]
                groups_to_skip.update(arg_indices)
                if any(answer_subparts[j] == [] for j in arg_indices):
                    continue
                arg_sets = tree_search([],
                                       [answer_subparts[ai] for ai in arg_indices],
                                       combination_func=lambda s, w: s + [w])
                for arg_set in arg_sets:
                    arg_set += [length]
                    answer_subparts[i].extend(list(FUNCTIONS[func](*arg_set)))
                if len(answer_subparts[i]) == 0:
                    answer_subparts[i] == ['']
            elif kind == 'lit':
                answer_subparts[i] = [phrase.replace(' ', '')]
            elif kind == 'null':
                answer_subparts[i] = ['']
            elif kind == 'first':
                answer_subparts[i] = [phrase[0]]
            elif kind == 'syn':
                syns = SYNONYMS[phrase.replace(' ', '_')]
                if len(syns) == 0:
                    syns = [phrase]
                answer_subparts[i] = list(syns)
    potential_answers = set(tree_search('', answer_subparts,
                                    lambda x: x not in groups_to_skip,
                                    lambda x: len(x) <= length and x in INITIAL_NGRAMS[len(x)] and matches_pattern(x, pattern)))
    answers = [(s, semantic_similarity(s, definition)) for s in potential_answers if s in WORDS and len(s) == length]
    return sorted(answers, key=lambda x: x[1], reverse=True)


def solve_phrases(phrases):
    pattern = phrases.pop()
    length = phrases.pop()
    answers = set([])
    answers_with_clues = []
    for clue in generate_structured_clues(phrases, length, pattern):
        new_answers = solve_structured_clue(clue)
        good_answers = [a for a in new_answers if a[1] > THRESHOLD]
        # if len(good_answers) > 0:
        #     print clue
        #     print good_answers
        new_answers = [a for a in new_answers if a not in answers]
        answers.update(new_answers)
        answers_with_clues.extend(zip(new_answers, [clue] * len(new_answers)))
    return sorted(answers_with_clues, key=lambda x: x[0][1], reverse=True)


if __name__ == '__main__':
    # print solve_structured_clue([('join', 'd'), ('trio of', 'sub_r'), ('astronomers', 'lit'), ('in', 'ins'), ('marsh', 'syn'), 6, 'f.....'])
    for phrases in all_phrases:
        print phrases
        answers = solve_phrases(phrases)[:50]
        for a in answers:
            print a
        print "\n"

