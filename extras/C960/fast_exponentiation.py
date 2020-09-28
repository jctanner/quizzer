#!/usr/bin/env python


def fe(x, y, debug=False):
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
        if debug:
            print('\tp=%s r=%s s=%s' % (p, r, s))

    return p


def main():
    x = 3
    y = 13
    res = fe(x,y, debug=True)
    print(res)




if __name__ == "__main__":
    main()
