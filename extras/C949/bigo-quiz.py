#!/usr/bin/env python3

import os
import random

SORTS = {
    'bubble sort': 'O(N^2)',
    'selection sort': 'O(N^2)',
    'insertion sort': 'O(N^2)',
    'shell sort': 'O(N^1.5)',
    'quick sort': 'O(N logN)',
    'merge sort': 'O(N logN)',
    'heap sort': 'O(N logN)',
    'radix sort': 'O(N)',
}


def main():
    keys = list(SORTS.keys())
    vals = sorted(set(SORTS.values()))

    answers = []
    for i in range(1, len(keys)):
        os.system('clear')
        print('--------------------------')
        print(i)
        thiskey = random.choice(keys)

        print(thiskey)
        for idx,choice in enumerate(vals):
            print('\t%s. %s' % (idx, choice))
        print('')

        answer = None
        while answer is None or not answer.isdigit():
            answer = input("Which formula?: ")
        answers.append((thiskey, vals[int(answer)]))
    
    print('')
    print('===============================')
    score = 0
    for idx,answer in enumerate(answers):
        #print(answer)
        if answer[1] == SORTS[answer[0]]:
            score += 1
        else:
            print('%s != %s ... %s' % (answer[0], answer[1], SORTS[answer[0]]))


    percent = float(score) / float(len(answers))
    print('YOU SCORED: %s%%' % (percent * 100))


if __name__ == "__main__":
    main()
