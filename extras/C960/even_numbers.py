#!/usr/bin/env python

from itertools import combinations
from itertools import permutations

#TOTAL = 5
#NUMBERS = [4,6,7,2,8]
#COMBINATIONS = []


def get_selection(prefix=None, choices=None, count=None, results=None):
    if results is None:
        results = []

    if len(prefix) == count:
        results.append(''.join(sorted(prefix)))
    else:
        total = count - len(prefix)
        for Y in range(0, len(choices)):
            for x in range(total, 0, -1):
                thisprefix = prefix + str(choices[Y])*x
                if len(thisprefix) == count:
                    results.append(''.join(thisprefix))
                else:
                    results += get_selection(prefix=thisprefix, choices=choices, count=count)

    return sorted(set(results))


def main():

    #global TOTAL
    #total = 4

    '''
    numbers = [4,6,7,2,8]
    perms = [x for x in permutations(numbers, 5)]
    combs = [x for x in combinations(numbers, 5)]
    '''

    numbers = [x for x in range(0, 10)]
    count = 4
    print('choices: %s' % numbers)
    combs = [
                int(x) for x in
                get_selection(prefix='', choices=numbers, count=count)
                if len(str(int(x))) == 4
            ]
    combs = sorted(set(combs))
    #print(combs)
    #combs = [int(x) for x in sorted(set(COMBINATIONS))]
    #combs = [int(x) for x in sorted(COMBINATIONS)]
    #print(combs)
    even = [x for x in combs if x % 2 == 0]
    odd = [x for x in combs if x % 2 != 0]

    even_last = [str(x)[-1] for x in even]
    even_last = sorted(set(even_last))
    odd_last = [str(x)[-1] for x in odd]
    odd_last = sorted(set(odd_last))

    print('total %s digit combinations: %s' % (count, len(combs)))
    print('total even %s digit combinations: %s' % (count, len(even)))
    print('total odd %s digit combinations: %s' % (count, len(odd)))
    print('last digits for even: %s' % even_last)
    print('last digits for odd: %s' % odd_last)
    #import epdb; epdb.st()


if __name__ == "__main__":
    main()
