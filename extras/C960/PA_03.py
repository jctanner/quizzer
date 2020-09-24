#!/usr/bin/env python


def main():
    x = 2
    count = 4

    print('%s. %s' % (count, x))
    while count > 0:
        x = 2 * x
        count = count - 1
        print('%s. %s' % (count, x))


if __name__ == "__main__":
    main()