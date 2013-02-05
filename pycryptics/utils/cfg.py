import nltk.grammar as gram
from nltk import parse
from nltk.tree import Tree
from pycryptics.utils.indicators import INDICATORS

"""
A Context Free Grammar (CFG) to describe allowed structures of cryptic crossword clues.
"""


top = gram.Nonterminal('top')
lit = gram.Nonterminal('lit')
d = gram.Nonterminal('d')
syn = gram.Nonterminal('syn')
first = gram.Nonterminal('first')
null = gram.Nonterminal('null')
ana = gram.Nonterminal('ana')
sub = gram.Nonterminal('sub')
ins = gram.Nonterminal('ins')
rev = gram.Nonterminal('rev')
ana_ = gram.Nonterminal('ana_')
sub_ = gram.Nonterminal('sub_')
ins_ = gram.Nonterminal('ins_')
rev_ = gram.Nonterminal('rev_')

# clue_arg = gram.Nonterminal('clue_arg')
clue_members = [lit, syn, first, null, ana, sub, ins, rev]

# ins_arg = gram.Nonterminal('ins_arg')
ins_members = [lit, ana, syn, sub, first, rev]

# ana_arg = gram.Nonterminal('ana_arg')
ana_members = [lit]

# sub_arg = gram.Nonterminal('sub_arg')
sub_members = [lit, syn, rev]

# rev_arg = gram.Nonterminal('rev_arg')
rev_members = [lit, syn]

known_functions = {
'in': [ins_, lit, null, sub_],
'a': [lit, syn, null],
'is': [null, lit],
'for': [null, syn],
'large': [first, syn],
'primarily': [sub_],
'and': [null, lit],
'of': [null],
'with': [null, ins_]}


def check_clue_totals(clue):
    if clue.count(ana) > 1:
        return False
    if all(c == null for c in clue):
        return False
    if clue.count('ins') > 1:
        return False
    return True

max_sub_parts = 3
base_clue_rules = [[clue_members] * i for i in range(max_sub_parts + 1)]

base_clue_rules.extend([[[sub_]] + [[first]] * i for i in range(max_sub_parts + 1, 8)])
base_clue_rules.extend([[[first]] * i + [[sub_]] for i in range(max_sub_parts + 1, 8)])
clue_rules = []
for r in base_clue_rules:
    clue_rules.append(r + [[d]])
    clue_rules.append([[d]] + r)

base_prods = []

expanded_prod_rules = {
ins: [[ins_members, [ins_], ins_members], [ins_members, ins_members, [ins_]]],
ana: [[ana_members, [ana_]], [[ana_], ana_members]],
sub: [[sub_members, [sub_]], [[sub_], sub_members]],
rev: [[rev_members, [rev_]], [[rev_], rev_members]],
top: clue_rules
}

for n, rules in expanded_prod_rules.items():
    for r in rules:
        rule_set = [[]]
        for el in r:
            new_rule_set = []
            for p in rule_set:
                for arg in el:
                    new_rule_set.append(p + [arg])
            rule_set = new_rule_set
        for rule in rule_set:
            base_prods.append(gram.Production(n, rule))

def generate_grammar(phrases):
    prods = []
    for p in phrases:
        if p in known_functions:
            tags = known_functions[p]
        else:
            found = False
            tags = [lit, d, syn, first]
            for kind in INDICATORS:
                if any(w == p or (len(w) > 5 and abs(len(w) - len(p)) <= 3 and p.startswith(w[:-3])) for w in INDICATORS[kind]):
                    tags.append(gram.Nonterminal(kind))
                    found = True
            if not found:
                # tags = word_tags
                tags = [lit, d, syn, first, ana_, sub_, rev_]
        for t in tags:
            prods.append(gram.Production(t, [p]))
    return gram.ContextFreeGrammar(top, base_prods + prods)


def clue_from_tree(tree):
    if not isinstance(tree, Tree):
        return tree
    elif "_arg" in tree.node:
        return clue_from_tree(tree[0])
    else:
        return tuple([tree.node] + [clue_from_tree(t) for t in tree])


def generate_clues(phrases):
    g = generate_grammar(phrases)
    parser = parse.EarleyChartParser(g)
    return [clue_from_tree(t) for t in parser.nbest_parse(phrases)]
