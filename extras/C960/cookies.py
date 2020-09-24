#!/usr/bin/env python

from pprint import pprint

TOTAL = 15
COOKIES = ['A','B', 'C', 'D']


COMBINATIONS = []

def get_selection(prefix=None, count=TOTAL):
    global COMBINATIONS

    if len(prefix) == count:
        COMBINATIONS.append(''.join(sorted(prefix)))
        return
    total = TOTAL - len(prefix)
    cookies = [x for x in COOKIES if x not in prefix]
    #print(flavors)

    for Y in range(0, len(cookies)):
        for x in range(total, 0, -1):
            thisprefix = prefix + cookies[Y]*x
            if len(thisprefix) == TOTAL:
                print(thisprefix)
                COMBINATIONS.append(''.join(sorted(thisprefix)))
            else:
                get_selection(prefix=thisprefix)

def main():
    get_selection(prefix='')
    #print(COMBINATIONS[:10])
    #print(COMBINATIONS[-10:])
    combos = sorted(COMBINATIONS)
    unique_combos = sorted(set(COMBINATIONS))

    sums = []
    for uc in unique_combos:
        thissum = {}
        for cookie in COOKIES:
            thissum[cookie] = len([x for x in uc if x == cookie])
        #if 0 in thissum.values():
        #    continue
        sums.append(thissum)

    string_sums = [str(x) for x in sums]
    string_sums = sorted(set(string_sums))
    #import epdb; epdb.st()

    print('total: %s' % len(combos))
    print('unique: %s' % len(unique_combos))
    print('hashes: %s' % len(string_sums))

    pprint(string_sums[:10])
    pprint(string_sums[-10:])


if __name__ == "__main__":
    main()