#!/usr/bin/env python

TOTAL = 24
FLAVORS = ['A','B', 'C', 'D', 'E', 'F']

COMBINATIONS = []

def get_selection(prefix=None, count=TOTAL):
    global COMBINATIONS

    if len(prefix) == count:
        COMBINATIONS.append(''.join(sorted(prefix)))
        return
    total = TOTAL - len(prefix)
    flavors = [x for x in FLAVORS if x not in prefix]
    #print(flavors)

    for Y in range(0, len(flavors)):
        for x in range(total, 0, -1):
            thisprefix = prefix + flavors[Y]*x
            if len(thisprefix) == TOTAL:
                print(thisprefix)
                COMBINATIONS.append(''.join(sorted(thisprefix)))
            else:
                get_selection(prefix=thisprefix)

def main():
    
    '''
    for Y in range(0, len(FLAVORS) - 1):
        print(Y)
        for x in range(TOTAL, 1, -1):
            print(FLAVORS[Y]*x)
            get_selection(prefix=FLAVORS[Y]*x)
    '''
    get_selection(prefix='')
    print(COMBINATIONS[:10])
    print(COMBINATIONS[-10:])
    combos = sorted(COMBINATIONS)
    unique_combos = sorted(set(COMBINATIONS))

    sums = []
    for uc in unique_combos:
        thissum = {}
        for flavor in FLAVORS:
            thissum[flavor] = len([x for x in uc if x == flavor])

        sums.append(thissum)

    string_sums = [str(x) for x in sums]
    string_sums = sorted(set(string_sums))
    #import epdb; epdb.st()

    print('total: %s' % len(combos))
    print('unique: %s' % len(unique_combos))
    print('hashes: %s' % len(string_sums))

if __name__ == "__main__":
    main()