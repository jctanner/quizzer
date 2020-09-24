#!/usr/bin/env python

import sys

def main():
    S =  [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    x = 2
    while x < 11:
        sys.stdout.write(str(x) + '.  ')
        for i in S[:]:
            sys.stdout.write(' ' + str(i))
            if i % x == 0 and i != x:
                sys.stdout.write('x')
                S.remove(i)
        x = x + 1
        print('')
    
    print(S)
    

if __name__ == "__main__":
    main()
