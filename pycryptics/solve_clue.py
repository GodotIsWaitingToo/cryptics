from __future__ import division
from pycryptics.utils.language import semantic_similarity
from pycryptics.grammar.cfg import generate_clues
from pycryptics.utils.phrasings import phrasings
from pycryptics.utils.synonyms import SYNONYMS
from pycryptics.grammar.clue_tree import ClueUnsolvableError
from collections import namedtuple
import re


Phrasing = namedtuple('Phrasing', 'phrases lengths pattern known_answer')

# Constraints = namedtuple('Constraints', 'lengths pattern known_answer')

class AnnotatedAnswer:
    def __init__(self, ans, clue):
        self.answer = ans.encode('ascii', 'replace')
        self.clue = clue
        d_tree = clue[[x.node for x in clue].index('d')]
        self.definition = d_tree[0]
        self.similarity = semantic_similarity(self.answer, self.definition)

    def __cmp__(self, other):
        return cmp((self.similarity, self.answer), (other.similarity, other.answer))

    def __str__(self):
        return str([self.answer, self.similarity, self.clue.derivations(self.answer)])

    def derivation(self):
        return "{:.0%}: ".format(self.similarity) + self.clue.derivations(self.answer)

    def long_derivation(self):
        return self.clue.long_derivation(self.answer, self.similarity)


class PatternAnswer(AnnotatedAnswer):
    def __init__(self, ans, phrasing):
        self.answer = ans
        sim0 = semantic_similarity(ans, phrasing[0])
        sim1 = semantic_similarity(ans, phrasing[-1])
        if sim0 > sim1:
            self.definition = phrasing[0]
        else:
            self.definition = phrasing[1]
        self.similarity = max(sim0, sim1)
        self.clue = "???"

    def __str__(self):
        return str([self.answer, self.similarity, self.clue])

    def derivation(self):
        return "???"

    def long_derivation(self):
        return "I don't understand the wordplay for this clue, but {} matches '{}' with confidence score {:.1%}".format(self.answer.upper(), self.definition, self.similarity)

class ClueSolutions:
    def __init__(self, anns):
        self.answer_scores = dict()
        self.answer_derivations = dict()
        for ann in anns:
            self.answer_derivations.setdefault(ann.answer, []).append(ann)
        for k, v in self.answer_derivations.items():
            self.answer_scores[k] = max(a.similarity for a in v)

    def sorted_answers(self):
        return sorted([(v, k) for k, v in self.answer_scores.items()], reverse=True)


def arg_filter(arg_set):
    if arg_set != [""]:
        return [a for a in arg_set if not a == ""]
    return arg_set


class CrypticClueSolver(object):
    def __init__(self):
        self.running = False
        self.answers_with_clues = None
        self.clue_text = None
        self.phrasing = None
        self.memo = {}

    def __enter__(self):
        # self.start_go_server()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()
        # self.stop_go_server()

    def stop(self):
        self.running = False

    def setup(self, clue_text):
        self.clue_text = clue_text
        self.memo = {}

    def run(self):
        self.running = True
        self.clue_text = self.clue_text.encode('ascii', 'ignore')
        all_phrasings, lengths, pattern, answer = parse_clue_text(self.clue_text)
        self.answers_with_clues = []

        for p in all_phrasings:
            self.phrasing = Phrasing(p, lengths, pattern, answer)
            if not self.running:
                break
            print p
            for ann_ans in self.solve_phrasing(p):
                self.answers_with_clues.append(ann_ans)
        if len(self.answers_with_clues) == 0 and pattern.replace('.', '') != "":
            self.answers_with_clues = [PatternAnswer(x, all_phrasings[0]) for x in SYNONYMS if matches_pattern(x, pattern, lengths)]
        self.answers_with_clues.sort(reverse=True)
        return self.answers_with_clues

    def solve_phrasing(self, phrasing):
        """
        Solve a clue which has been broken down into phrases, like:
        ['initially', 'babies', 'are', 'naked']
        """
        answers_with_clues = []
        possible_clues = list(generate_clues(phrasing))

        for i, clue in enumerate(possible_clues):
            if not self.running:
                break
            # print "solving:", clue
            try:
                answers = clue.get_answers(clue, self.phrasing)
                # answers = self.get_answers(clue)
            except ClueUnsolvableError:
                answers = []
            for answer in answers:
                if answer in phrasing or any(x.startswith(answer) for x in phrasing) or any(answer == x for p in phrasing for x in p.split('_')):
                    pass
                else:
                    answers_with_clues.append(AnnotatedAnswer(answer, clue))
        return sorted(answers_with_clues, reverse=True)

    def collect_answers(self):
        if self.answers_with_clues is not None:
            return ClueSolutions(self.answers_with_clues)

    # def get_answers(self, t):
    #     if isinstance(t, str):
    #         return [t]

    #     # t_hash = t._pprint_flat('', '()', '"')
    #     # if t_hash in self.memo:
    #     #     t.answers = self.memo[t_hash]
    #     if t.answers is None:
    #         t.answers = {}
    #         self.solve_clue_tree(t)
    #     if t.answers == {}:
    #         # print "clue:", t, "unsolvable"
    #         raise ClueUnsolvableError
    #     # print "solved:", t, "\ngot:", t.answers
    #     # self.memo[t_hash] = t.answers
    #     return t.answers

    # def solve_clue_tree(self, t):
    #     child_answers = [self.get_answers(c) for c in t]
    #     for i, s in enumerate(child_answers):
    #         if isinstance(s, dict):
    #             child_answers[i] = s.keys()
    #     if t.node == 'top':
    #         arg_sets = self.make_top_arg_sets(child_answers)
    #     else:
    #         arg_sets = self.make_arg_sets(child_answers)
    #     for args in arg_sets:
    #         answers = RULES[t.node](arg_filter(args), self.phrasing)
    #         if answers is None:
    #             answers = []
    #         for ans in answers:
    #             t.answers[ans] = args[:]

    # def make_top_arg_sets(self, child_answers):
    #     target_len = sum(self.phrasing.lengths)
    #     arg_sets = [([], 0, '')]
    #     for ans_list in child_answers:
    #         new_arg_sets = []
    #         for ans in ans_list:
    #             for s in arg_sets:
    #                 candidate = (s[0] + [ans], s[1] + len(ans), s[2] + ans)
    #                 if valid_partial_answer(candidate[2], self.phrasing):
    #                 # if candidate[1] <= target_len:
    #                     new_arg_sets.append(candidate)
    #         arg_sets = new_arg_sets
    #     return [s[0] for s in arg_sets if s[1] == target_len]

    # def make_arg_sets(self, child_answers):
    #     # return itertools.product(*child_answers)
    #     arg_sets = [[]]
    #     for ans_list in child_answers:
    #         new_arg_sets = []
    #         for ans in ans_list:
    #             for s in arg_sets:
    #                 new_arg_sets.append(s + [ans])
    #         arg_sets = new_arg_sets
    #     return arg_sets


def matches_pattern(word, pattern, lengths):
    return (tuple(len(x) for x in word.split('_')) == lengths) and all(c == pattern[i] or pattern[i] == '.' for i, c in enumerate(word.replace('_', '')))


def split_clue_text(clue_text):
    clue_text = clue_text.encode('ascii', 'ignore')
    if '|' not in clue_text:
        clue_text += ' |'
    clue_text = clue_text.lower()
    clue, paren, rest = clue_text.rpartition('(')
    lengths, rest = rest.split(')')
    lengths = lengths.replace('-', ',')
    lengths = tuple(int(x) for x in lengths.split(','))
    pattern, answer = rest.split('|')
    pattern = pattern.strip()
    clue = re.sub('-', '_', clue)
    clue = re.sub(r'[^a-zA-Z\ _0-9]', '', clue)
    clue = re.sub(r'\ +', ' ', clue)
    phrases = clue.split(' ')
    phrases = [p for p in phrases if p.strip() != '' and p.strip() != '_']
    return phrases, lengths, pattern, answer


def parse_clue_text(clue_text):
    phrases, lengths, pattern, answer = split_clue_text(clue_text)
    return phrasings(phrases), lengths, pattern, answer


if __name__ == '__main__':
    # clue = "spin broken shingle (7)"
    # clue = "sink graduate with sin (5)"
    # clue = "you finally beat iowa perfect world (6)"
    # clue = "be aware of nerd's flip_flop (4) k..."
    # clue = "Bottomless sea, stormy sea - waters' surface rises_and_falls (7) s.es..."
    clue = "gratuitous indicators on_top_of screen (8) n....... | NEEDLESS"
    # phrasing = Phrasing([],(7,),'s.es...')
    # print valid_partial_answer('se', phrasing)
    with CrypticClueSolver() as solver:
        solver.setup(clue)
        answers = solver.run()
        print answers[0].long_derivation()
        # for a in answers[:5]: print a

