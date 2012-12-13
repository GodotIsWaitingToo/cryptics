

def tree_search(branching_list, start=[[]], branch_index_test=lambda x: True,
                member_test=lambda x: True,
                combination_func=None):
    """
    A general tool for figuring out all the ways to combine a bunch of lists.

    Say we have branching_list = [['a', 'b'], ['c', 'd']].
    Then tree_search('', branching_list) would return:
    ['ac', 'ad', 'bc', 'bd']
    """
    if combination_func is None:
        if isinstance(start[0], list):
            combination_func = lambda s, w: s + [w]
        else:
            combination_func = lambda s, w: s + w

    active_set = start
    for i, part in enumerate(branching_list):
        if not branch_index_test(i):
            continue
        new_active_set = []
        for s in active_set:
            for w in part:
                candidate = combination_func(s, w)
                if member_test(candidate):
                    new_active_set.append(candidate)
        active_set = new_active_set
    return active_set
