#!/usr/bin/env python3

import string
import sys

from pprint import pprint


def ALPHABET():
    letter_map = {}
    for idl,letter in enumerate(string.ascii_lowercase):
        letter_map[letter] = idl + 65

    return letter_map


def word_to_numeric_plaintext(word):

    '''convert a word to the plaintext numeric from'''

    lm = ALPHABET()
    word = word.lower()
    result = ''

    for char in word:
        key = str(lm[char])
        if len(key) == 1:
            key = '0' + key
        result += key

    return result


def digits_to_word(digits):

    '''convert a word to the plaintext numeric from'''

    lm = ALPHABET()

    digits = str(digits)
    if len(digits) % 2 != 0:
        digits = '0' + digits

    if len(digits) < 3:
        for k,v in lm.items():
            if v == int(digits):
                return k
    else:
        print('digits: %s' % digits)
        word = ''
        for idx in range(0, len(digits), 2):
            print('idx: %s' % idx)
            thisbit = digits[idx:idx+2]
            thisbit = int(thisbit)
            for k,v in lm.items():
                if v == thisbit:
                    word += k
                    break
        return word


def split_msg(msg, N):

    '''split message so each part's int val is less than N'''

    def total(bits):
        this_total = ''
        for bit in bits:
            this_bit = word_to_numeric_plaintext(bit)
            #print(this_bit)
            this_total += this_bit
        if not this_total:
            import epdb; epdb.st()
        #print(this_total)
        return int(this_total)

    splits = []

    start = 0
    end = 1
    while total(msg[start:end]) < N and end <= len(msg):
        print('')
        print('start: %s' % start)
        print('end: %s' % end)
        end += 1
        current_msg = ''.join(msg[start:end])
        current_total = total(msg[start:end])
        print('current: %s total:%s' % (current_msg, current_total))

        if current_total > N:
            splits.append([start,end-1, total(msg[start:end-1]), msg[start:end-1]])
            pprint(splits)
            start = end - 1
            end = start + 1
            print('new start: %s new end: %s --> %s' % (start, end, msg[start:end]))
        
        if end == (len(msg) + 1):
            splits.append([start,end-1, total( msg[start:end-1]), msg[start:end-1]])
            #import epdb; epdb.st()
            break


    pprint(splits)
    splits = [x[-1] for x in splits]
    #import epdb; epdb.st()
    return splits


def fast_modular_exponentiation(x, y, n): 
    p = 1 
    s = x 
    r = y 

    count = 0 
    while (r > 0): 
        #print('%s: %r mod 2 == %s' % (count, r, r % 2))
        print('%s: r:%s s:%s p:%s n:%s' % (count, r, s, p, n)) 
        if (r % 2 == 1): 
            p = (p * s) % n 
        s = (s * s) % n 
        r = int(r / 2)
        count += 1
        #print('%s: p=%s r=%s' % (count, p, r))

    return p

def encrypt(m, e, N, ignore=False):
    # c = m^e mod N -->
    if not ignore:
        assert m < N, "m has to be < N"

    ## YOU CAN'T JUST PLUG THIS IN BECAUSE PYTHON DOESN'T DEAL WITH LARGE exponents !!!
    #c = (m^e) % N
    #print('%s^%s mod %s == %s' % (m, e, N, c))

    # USE FAST EXPO INSTEAD!!!
    p = fast_modular_exponentiation(m, e, N)
    #import epdb; epdb.st()

    return p


def decrypt(c, d, N):
    #msg = (c^d) % N
    msg = fast_modular_exponentiation(c, d, N)
    print('%s^%s mod %s == %s' % (c,d,N, msg))

    return msg


def main():
    #print(ALPHABET())

    #msg = "HITHERE"
    #msg = "camera"
    msg = "password"
    sys.stdout.write('           ')
    for x in msg:
        sys.stdout.write(' ' + x)
    sys.stdout.write('\n')
    pt = word_to_numeric_plaintext(msg)
    print('plaintext: %s' % pt)
    pt = int(pt)

    p = 3
    d = p
    q = 11
    e = 7
    N = p * q
    phi = (p - 1)*(q - 1)
    
    d = 84173
    N = 373097
    e = 459173
    phi = None

    print('e: %s' % e)
    print('N: %s' % N)
    print('phi: %s' % phi)

    if pt > N and len(msg) > 1:
        if N < 100:
            msgs = split_msg(msg, 10000)
        else:
            msgs = split_msg(msg, N)
        print('%s split to %s' % (msg, msgs))
    else:
        msgs = [msg]

    pprint(msgs)
    ciphers = []
    for _msg in msgs:
        print('MSG: %s' % _msg)
        _pt = word_to_numeric_plaintext(_msg)
        print('PT: %s' % _pt)
        _pt = int(_pt)
        cipher = encrypt(_pt, e, N, ignore=True)
        print('ciphertext: %s' % cipher)
        ciphers.append(cipher)

    print('------------------------ ENCRYPTION')
    pprint(ciphers)

    print('------------------------ DECRYPTION')
    final_msg = ''
    for cipher in ciphers:
        print('cipher: %s' % cipher)
        digits = decrypt(cipher, d, N)
        print('c:%s decrypted to %s' % (cipher, digits))
        word = digits_to_word(digits)
        print('c:%s -> d:%s -> m:%s' % (cipher, digits, word))
        final_msg += word
    print('FINAL: %s' % final_msg)


if __name__ == "__main__":
    main()