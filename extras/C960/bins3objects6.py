#!/usr/bin/env python

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
    #objects = list(range(0,6))
    bins = list(range(0,3))
    bins = [chr(65+x) for x in bins]
    results = get_selection(choices=bins, count=6)
    results = [''.join(sorted(x)) for x in results]
    results = sorted(set(results))

    for idx,x in enumerate(results):
        print(f'{idx+1}. {x}')

    print('-' * 30)
    print(f'{len(results)} total ways to sort 6 items into 3 bins')
    print('')
    print('')
    print('This is a multiset counting problem: use the formula nCr(n+m-1, m-1).')
    print('n = 6')
    print('m = 3')
    print('nCr(6+3-1, 3-1) -> nCr(8,2) -> 28')
    #import epdb; epdb.st()


if __name__ == "__main__":
    main()
