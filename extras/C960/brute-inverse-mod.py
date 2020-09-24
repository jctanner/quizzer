#!/usr/bin/env python3

def brute_inverse(x,n):
    for z in range(1,max([x,n])*2):
        a = (z * x) % n
        b = ((0-z) * x) % n
        if (a == 1):
            print('\t %s*%s mod %s == 1' % (z, x, n))
        if (b == 1):
            print('\t -%s*%s mod %s == 1' % (z, x, n))

def main():
    print('s*x mod n == 1')
    print('')
    x = int(input('x= '))
    n = int(input('n= '))

    ir = brute_inverse(x,n)


if __name__ == "__main__":
    main()
