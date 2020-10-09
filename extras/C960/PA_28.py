#!/usr/bin/env python

from pprint import pprint


def main():
    results = [
        [3], 
        [3], 
        [3],
        [3],
        [3],
        [3]
    ]

    count = 0
    while count < 5:
        count += 1
        i = count - 1

        #print('-' * 10)
        for sc in range(0,6):
            if i == 0:
                continue
            '''
            eqs = [
                2 * results[i-1][0],
                2 * results[i-1][1] - 1,
                2 + 2*i,
                3 + i * (2**1),
                1 + 2*(i + 1),
                3 + i * 2**(i+1)
            ]
            results.append(eqs)
            '''
            #print(sc)
            if sc == 0:
                b = results[sc][i-1]
                res = (2 * b) - 1
                results[sc].append(res)
            elif sc == 1:
                b = results[sc][i-1]
                res = 2 * (b - 1)
                results[sc].append(res)
            elif sc == 2:
                res = 2 + (2*i)
                results[sc].append(res)
            elif sc == 3:
                res = 3 + (i * (2**i))
                results[sc].append(res)
            # right answer? ...
            elif sc == 4:
                print('--------------------------')
                res = 1 + (2 ** (i + 1))
                print(f'\t1 + 2*(i+1) = {res}')
                print(f'\t1 + 2*({i}+1) = {res}')
                print(f'\t1 + 2*({i+1}) = {res}')
                print(f'\t1 + {2*(i+1)} = {res}')
                results[sc].append(res)
            elif sc == 5:
                res = 3 + (i * (2**(i + 1)))
                results[sc].append(res)

    #pprint(results)
    for idx,x in enumerate(results):
        print(f'{idx}. {x} sum={sum(x)}')

    print('')
    print(f'expected: #{1+3} ... {results[1+3]} sum={sum(results[1+3])}')


if __name__ == "__main__":
    main()
