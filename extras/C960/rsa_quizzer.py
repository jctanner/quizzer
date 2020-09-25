#!/usr/bin/env python

import random

from pprint import pprint
import rsa_common as rc


def get_data():
    ds = {}
    ds['q'],ds['p'] = rc.getCoPrimes(minimum=1, maximum=20)

    #coprimes = rc.findCoPrimes(ds['p'])
    #ds['q'] = random.choice(coprimes)           

    ds['phi'] = (ds['q'] - 1) * (ds['p'] - 1)

    ds['N'] = ds['q'] * ds['p']

    es = rc.findCoPrimes(ds['phi'])
    ds['e'] = random.choice(es)

    ds['d'] = rc.get_multiplicative_inverse(ds['e'], ds['phi'])

    return ds


def get_random_word():
    chars = list(range(ord("a"), ord("z")))
    '''
    word = ''
    for x in range(0, random.choice([2])):
        word += chr(random.choice(chars))
    return word.upper()
    '''
    return chr(random.choice(chars)).upper()


def main():
    ds = get_data()
    pprint(ds)

    while True:
        ans = input(f"given p={ds['p']} and q={ds['q']}, what is N? ")
        if ans.strip() == str(ds['N']):
            break
        print('Incorrect, try again.')
    
    while True:
        ans = input(f"given p={ds['p']} and q={ds['q']}, what is phi? ")
        if ans.strip() == str(ds['phi']):
            break
        print('Incorrect, try again.')

    while True:
        ans = input(f"given phi={ds['phi']} what is a valid value for e? ")
        if rc.isCoPrime(ds['phi'], int(ans)):
            break
        print('Incorrect, try again.')
    
    # ds['d'] = rc.get_multiplicative_inverse(ds['e'], ds['phi'])
    while True:
        ans = input(f"Given p={ds['p']} q={ds['q']} N={ds['N']} and e={ds['e']} what is d? ")
        if ans.strip() == str(ds['d']):
            break
        print('Incorrect, try again.')

    while True:
        ans = input('What two variables make up the pubkey?: ')
        if sorted(ans.strip().lower().replace(' ', '')) == ['e','n']:
            break
        print('Incorrect, try again.')
    
    while True:
        ans = input('What variable is the private key?: ')
        if ans.strip().lower() == 'd':
            break
        print('Incorrect, try again.')

    word = get_random_word()
    enc = int(rc.encode_message(word))
    encrypted = (enc ** ds['e']) % ds['N']

    while True:
        ans = input(f"Given the encoded '{word}' as M={enc} and N={ds['N']} and e={ds['e']} what is C? ")
        if ans.strip() == str(encrypted):
            break
        print('Incorrect, try again.')
    
    word = get_random_word()
    enc = int(rc.encode_message(word))
    encrypted = (enc ** ds['e']) % ds['N']

    count = 0
    while True:
        ans = input(f"Given C={encrypted} and m={enc} and N={ds['N']} and e={ds['e']} and phi={ds['phi']} and d={ds['d']} what is M? ")
        if ans.strip() == str(enc):
            break
        count += 1
        if count > 3:
            print('too many attempts. Answer was: %s' % enc)
            break
        print('Incorrect, try again.')



if __name__ == "__main__":
    main()