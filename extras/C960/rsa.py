#!/usr/bin/env python3

import argparse
import random

import rsa_common as rc

def test():
    #p,q = rc.getCoPrimes(minimum=4000)
    p,q = rc.getCoPrimes(minimum=0, maximum=10)
    print('p=%s q=%s' % (p,q))

    N = p*q
    print('N=%s' % N)

    phi = (p-1)*(q-1)
    print('phi=%s' % phi)

    # e is coprime with phi .. aka gcd(e,phi) = 1
    es = rc.findCoPrimes(phi)
    e = random.choice(es)
    print('e=%s' % e)

    d = rc.get_multiplicative_inverse(e, phi)
    print('d=%s' % d)

    pubkey = (N, e)
    privkey = d

    message = 'ATTACK_AT_DAWN'
    enc = rc.encode_message(message)
    print('message:%s -> encoded:%s' % (message, enc))


    # cipher: c = m^e mod N
    #c = (int(enc)**e) % N
    c = rc.encrypt(int(enc), e, N, debug=True)
    print('cipher: %s' % c)

    '''
    # decrypt: c^d mod N
    decrypted = (c**d) % N
    print('decrypted: %s' % decrypted)
    '''
    pt = rc.decrypt(c, d, N, debug=True)
    print('decrypted: %s' % pt)


def get_missing_args(args):
    print(args)

    if not args.q and not args.p:
        args.q,args.p = rc.getCoPrimes()

    if not args.q and args.p:
        coprimes = rc.findCoPrimes(args.p)
        args.q = random.choice(coprimes)           

    if not args.p and args.q:
        coprimes = rc.findCoPrimes(args.q)
        args.p = random.choice(coprimes)           

    if not args.phi and args.q and args.p:
        args.phi = (args.q - 1) * (args.p - 1)

    if not args.N and args.q and args.p:
        args.N = args.q * args.p

    if not args.e:
        es = rc.findCoPrimes(args.phi)
        args.e = random.choice(es)

    if not args.d and args.e and args.phi:
        args.d = rc.get_multiplicative_inverse(args.e, args.phi)



def encode(args):
    print(args)
    enc = rc.encode_message(args.message)
    print('ENCODED: %s' % enc)


def encrypt(args):
    get_missing_args(args)
    pass

def encode_encrypt(args):
    get_missing_args(args)
    encoded = rc.encode_message(args.plaintext_message, offset=args.char_offset)


    print('p=%s' % args.p)
    print('q=%s' % args.q)
    print('phi=%s' % args.phi)
    print('N=%s' % args.N)
    print('e=%s' % args.e)
    print('d=%s' % args.d)

    print('encoded: %s' % encoded)

    cipher = rc.encrypt(int(encoded), args.e, args.N, debug=args.debug)
    print('cipher: %s' % cipher)


def decrypt(args):
    get_missing_args(args)
    encoded = rc.decrypt(int(args.cipher), args.d, args.N, debug=args.debug)
    print('encoded: %s' % encoded)
    message = rc.decode_message(encoded, offset=args.char_offset, debug=args.debug)
    print('message: %s' % message)


def add_common_args(parser):
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('-p', type=int)
    parser.add_argument('-q', type=int)
    parser.add_argument('-N', type=int)
    parser.add_argument('--phi', type=int)
    parser.add_argument('-e', type=int)
    parser.add_argument('-d', type=int)
    parser.add_argument('--char-offset', type=int, default=0)


def main():

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    encode_parser = subparsers.add_parser('encode', help='1')
    encode_parser.add_argument('message')
    encode_parser.set_defaults(func=encode)
    add_common_args(encode_parser)

    encrypt_parser = subparsers.add_parser('encrypt', help='2')
    encrypt_parser.add_argument('encoded')
    encrypt_parser.set_defaults(func=encrypt)
    add_common_args(encrypt_parser)

    ee_parser = subparsers.add_parser('encode_encrypt', help='3')
    ee_parser.add_argument('plaintext_message')
    ee_parser.set_defaults(func=encode_encrypt)
    add_common_args(ee_parser)

    decrypt_parser = subparsers.add_parser('decrypt', help='4')
    decrypt_parser.add_argument('cipher')
    decrypt_parser.set_defaults(func=decrypt)
    add_common_args(decrypt_parser)

    args = parser.parse_args()
    args.func(args)




if __name__ == "__main__":
    main()
