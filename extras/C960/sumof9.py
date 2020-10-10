#!/usr/bin/env python

from itertools import permutations

def get_selection(prefix='', choices=None, count=None, results=None):
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
    numbers = list(range(0,10))

    '''
    perms = [x for x in permutations(numbers, 3)]
    perms = [x for x in perms if sum(x) == 9]
    '''
    perms = get_selection(choices=numbers, count=3)
    perms = [[int(y) for y in x] for x in perms]
    perms = [x for x in perms if sum(x) == 9]
    #import epdb; epdb.st()

    for idx,x in enumerate(perms):
        print(f'{idx+1}. {x}')
    print('-' * 30)
    print(f'{len(perms)} total 3 number permuations with a sum of 9')
    #import epdb; epdb.st()


if __name__ == "__main__":
    main()
