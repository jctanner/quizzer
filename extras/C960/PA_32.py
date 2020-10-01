#!/usr/bin/env python

from itertools import combinations
from itertools import permutations

people = ['M', 'F', 'A', 'B', 'C']


def is_child(a):
    if a in ['A', 'B', 'C']:
        return True
    return False

def child_is_next_to_child(arr):
    #print(arr)
    for idx,x in enumerate(arr):
        #print(idx,x)
        if idx == len(arr) - 1:
            break
        if is_child(x) and is_child(arr[idx+1]):
            return True
        #if idx == len(arr) and is_child(x) and is_child(arr[x-1]):
        #    return True
    print(arr)
    return False

def main():
    people = ['M', 'F', 'A', 'B', 'C']
    #combos = [x for x in combinations(people, len(people))]
    perms = [x for x in permutations(people, len(people))]

    bad = [x for x in perms if child_is_next_to_child(x)]
    good = [x for x in perms if not child_is_next_to_child(x)]

    print('bad: %s' % len(bad))
    print('good: %s' % len(good))
    #import epdb; epdb.st()


if __name__ == "__main__":
    main()