#!/usr/bin/env python

import random

def factorial(n):
    if n == 0:
        return 1
    if n > 1:
        return n * factorial(n - 1)
    return n

def get_union_question():
    # S U H = |S| + |H| - [S union H]
    A = random.randrange(0, 50)
    B = random.randrange(0, 50)
    intersection = random.randrange(min([A,B]), max([A,B]))
    union = A + B - intersection
    return (A, B, intersection, union)


def get_n_choose_r_question(n=None, r=None):
    if n is None and r is None:
        a = random.randrange(0, 50)
        b = random.randrange(0, 50)
        n = max([a,b])
        r = min([a,b])

    res = factorial(n) / (factorial(r) * factorial(n-r))
    return (n, r, res)


def main():

    '''
    q = get_question()
    print('A = %s' % q[0])
    print('B = %s' % q[1])
    print('intersection of A and B = %s' % q[2])

    answer = input("What is the union of A and B?: ")
    if int(answer) == q[3]:
        print('Correct!')
    else:
        print('Incorrect ... %s' % q[3])
    '''

    print(factorial(7))
    print(get_n_choose_r_question(n=7, r=3))


if __name__ == "__main__":
    main()