import cPickle as pickle
from utils.cfg import generate_clues


def load_clue_structures():
    with open('data/clue_structures.pck', 'rb') as f:
        c = pickle.load(f)
    return c


CLUE_STRUCTURES = load_clue_structures()

def convert_indexed_clue(clue, phrases):
    if isinstance(clue, str):
        return clue
    elif isinstance(clue, int):
        return phrases[clue]
    else:
        return tuple([convert_indexed_clue(c, phrases) for c in clue])


def generate_cached_clues(phrases):
    if len(phrases) in CLUE_STRUCTURES:
        for indexed_clue in CLUE_STRUCTURES[len(phrases)]:
            yield convert_indexed_clue(indexed_clue, phrases)
    else:
        for c in generate_clues(phrases):
            yield c
