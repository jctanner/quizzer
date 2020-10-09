#!/usr/bin/env python

import math


def main():
    x = 1000
    print(x)
    while x > 0:
        x = math.log(x, 2)
        print(x)


if __name__ == "__main__":
    main()
