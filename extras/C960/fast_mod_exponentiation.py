#!/usr/bin/env python


def fe(x, y, n):
    p = 1
    s = x
    r = y

    count = 0
    while (r > 0):
        #print('%s: %r mod 2 == %s' % (count, r, r % 2))
        #print('%s: r:%s s:%s p:%s n:%s' % (count, r, s, p, n))
        if (r % 2 == 1):
            #print('%s %% 2 == 1' % (r))
            p = (p * s) % n
        s = (s * s) % n
        r = int(r / 2)
        count += 1
        #print('%s: p=%s r=%s' % (count, p, r))
        #print('%s: r:%s s:%s p:%s n:%s' % (count, r, s, p, n))
        print('%2d. \tr:%9d \ts:%9d \tp:%9d \tn:%9d' % (count, r, s, p, n))

    return p


def main():
    x = 3
    y = 13
    n = 7
    #x = 11
    #y = 20
    #n = 33

    #x = 5
    #y = 35
    #n = 11

    #x = 5
    #y = 68
    #n = 7

    #x = 78
    #y = 859
    #n = 1829

    #x = 7879
    #y = 459173
    #n = 373097

    print('--------------------------')
    print('x=%s y=%s n=%s' % (x,y,n))
    print('--------------------------')
    res = fe(x,y,n)
    print('--------------------------')
    print('final p: %s' % res)
    print('--------------------------')




if __name__ == "__main__":
    main()
