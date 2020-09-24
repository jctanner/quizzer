#!/usr/bin/env python


def fe(x, y):
    p = 1
    s = x
    r = y

    count = 0
    while (r > 0):
        print('%s: %r mod 2 == %s' % (count, r, r % 2))
        #print('%s: %s' % (count, s))
        if (r % 2 == 1):
            p = p * s
        s = s * s
        r = int(r / 2)
        count += 1
        #print('%s: p=%s r=%s' % (count, p, r))

    return p


def main():
    x = 3
    y = 13
    res = fe(x,y)
    print(res)




if __name__ == "__main__":
    main()
