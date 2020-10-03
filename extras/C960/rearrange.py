#!/usr/bin/env python

from itertools import combinations
from itertools import permutations

from pprint import pprint

#TOTAL = 5
#NUMBERS = [4,6,7,2,8]
#COMBINATIONS = []


def main():

    #global TOTAL
    #total = 4

    '''
    numbers = [4,6,7,2,8]
    perms = [x for x in permutations(numbers, 5)]
    combs = [x for x in combinations(numbers, 5)]
    '''

    letters = 'MASK'[:]
    count = len(letters)
    print('choices: %s' % letters)
    perms = [x for x in permutations(letters, count)]
    pprint(perms[0:10])

    #t3s = [x for x in perms if 'TTT' in ''.join(x)]
    #pprint(t3s[0:5] + ['...'] + t3s[-5:])
    #pprint(t3s[-10:])
    #pprint([x for x in t3s if ''.join(x).endswith('TTT')])

    print('total: %s' % len(perms))
    #print('total with TTT: %s' % len(t3s))
    #import epdb; epdb.st()


if __name__ == "__main__":
    main()
