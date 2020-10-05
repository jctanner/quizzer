#!/usr/bin/env python

import rsa_common as rc

#rsa_common.py:    res = get_multiplicative_inverse(*getCoPrimes())


def main():
    inverse = rc.get_multiplicative_inverse(13,33, debug=True)
    print('inverse: %s' % inverse)


if __name__ == "__main__":
    main()
