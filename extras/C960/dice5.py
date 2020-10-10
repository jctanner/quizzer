#!/usr/bin/env python

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
    sides = list(range(1,7))
    events = get_selection(prefix='', choices=sides, count=5)
    events = [[int(y) for y in x] for x in events]

    print(f'total events: {len(events)}')

    all2s = [x for x in events if sorted(set(x)) == [2]]
    all2sProb = len(all2s) / float(len(events))
    print(f'events with all 2: {len(all2s)}')
    print(f'probability all 2: {all2sProb}')

    four2s = [x for x in events if len([y for y in x if y == 2]) == 4]
    four2swithEnd1 = [x for x in four2s if x[-1] == 1]
    f2e1prob = len(four2swithEnd1) / float(len(events))
    print(f'events with four 2s and ends with 1: {len(four2swithEnd1)}')
    print(f'events with four 2s and ends with 1 probability: {f2e1prob}')

    notall2 = [x for x in events if sorted(set(x)) != [2]]
    notall2prob = len(notall2) / float(len(events))
    print(f'events with not all 2: {len(notall2)}')
    print(f'probability not all 2: {notall2prob}')
    import epdb; epdb.st()


if __name__ == "__main__":
    main()
