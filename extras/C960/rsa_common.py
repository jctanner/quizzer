#!/usr/bin/env python3

import random
import re

from pprint import pprint


def encrypt(encoded_int, e, N, debug=False):
    # use fast exponentiation ...
    # c = encoded_int^e mod N
    c = fast_exponentiation(encoded_int, e, N, debug=debug)
    return c


def decrypt(cipher, d, N, debug=False):
    # use fast exponentiation ...
    # pt = c^d mod N
    pt = fast_exponentiation(cipher, d, N, debug=debug)
    return pt


def get_charmap(offset=0):
    """
        Encode a message to numerical values
        per the zybook A=01 schema
    """

    # THE ZYBOOK RSA EXAMPLES USE OFFSET=64(65)
    CHARMAP = {}

    # use ordinal values to fill in a map
    counter = offset
    for x in range(ord('A'), ord('Z')+1):
        counter += 1
        scounter = str(counter)
        if len(scounter) == 1:
            scounter = '0' + scounter
        CHARMAP[chr(x)] = scounter
    CHARMAP['_'] = str(counter + 1)
    CHARMAP[' '] = str(counter + 2)
    return CHARMAP

def encode_message(message, offset=0):
    CHARMAP = get_charmap(offset=offset)

    # translate the message via the map
    encoded = ''
    for char in message:
        encoded += CHARMAP[char]

    # leading zeros should be stripped
    encoded = encoded.lstrip('0')

    return encoded

def decode_message(encoded, offset=0, debug=False):
    CHARMAP = get_charmap(offset=offset)

    encoded = str(encoded)
    if len(encoded) % 2 != 0:
        encoded = '0' + encoded

    n = 2
    chunks = [encoded[i:i+n] for i in range(0, len(encoded), n)]

    message = ''
    for chunk in chunks:
        for k,v in CHARMAP.items():
            if chunk == v:
                message += k
                if debug: print('%s --> %s' % (chunk, k))
                break
        if debug: print('%s was not in the charmap' % chunk)
    #import epdb; epdb.st()
    return message


def getCoPrimes(minimum=None, maximum=None):
    """
    Generate two random numbers that are coprime
    """

    if minimum and maximum:
        _primes = getPrimes(start=minimum, end=maximum)
    elif minimum:
        _primes = getPrimes(start=minimum)
    elif maximum:
        _primes = getPrimes(end=maximum)
    else:
        _primes = getPrimes()

    if minimum:
        _primes = [x for x in _primes if x > minimum]
    if maximum:
        _primes = [x for x in _primes if x <= maximum]
    while True:
        a = random.choice(_primes)
        b = random.choice(_primes)
        if a != b and isCoPrime(a, b):
            return a,b
    return None, None


def findCoPrimes(a, count=None):
    """
    Given a find coprime b
    """
    _primes = getPrimes()
    coprimes = []
    for x in _primes:
        if count and len(coprimes) >= count: 
            break
        if isCoPrime(a, x):
            coprimes.append(x)
    return coprimes


def test_findCoPrimes():
    assert findCoPrimes(3, count=3) == [5, 7, 11]


def getPrimes(count=100, start=1, end=None):
    """
    Make a list of prime numbers
    """
    primes = []
    counter = start
    while len(primes) < count:
        if end is not None and counter >= end:
            break
        if isPrime(counter):
            primes.append(counter)
        counter += 1
    return primes


def test_getPrimes():
    assert len(getPrimes(count=10)) == 10


def isPrime(x, debug=False):
    if x == 1:
        return True
    if x % 2 == 0:
        return False

    divisors = []
    for d in range(2, x-2):
        if x % d == 0:
            divisors.append(d) 

    if debug:
        print(divisors)

    if len(divisors) == 0:
        return True

    return False


def isCoPrime(x, y):
    """
    Do the two numbers have a GCD of 1?
    """
    if gcd(x, y) == 1:
        return True
    return False


def test_isCoPrime():
    assert isCoPrime(313, 431) == True


def gcd(a, b):

    t0 = max([a, b])
    t1 = min([a, b])

    p = None
    final_p = None
    while p is None or p > 1:
        if p == 1:
            break
        #print(p)
        p = t0 % t1
        if p > 0:
            final_p = p
        #print('%s %% %s == %s' % (t0, t1, p))
        t0 = t1
        t1 = p

    return final_p


def test_gcd():
    assert gcd(111, 4) == 1


def eval_coefficients(eq, multiply=1, depth=0, debug=False):
    # '((1*8)+(-1*((1*15)+(-1*8))))'
    # to
    #  1*8 + -1*15 + 1*8
    #  2*8 + -1*15


    def is_closed_form(exp):
        opens = [x for x in exp if x =='(']
        closes = [x for x in exp if x ==')']
        if len(opens) == len(closes):
            return True
        return False

    def split_eq_on_highest_addition(eq):
        plus_positions = [m.start() for m in re.finditer('\+', eq)]
        for plus_position in plus_positions:
            child1 = eq[:plus_position]
            child2 = eq[plus_position+1:]
            if all([is_closed_form(child) for child in [child1, child2]]):
                return [child1, child2]
        import epdb; epdb.st()
        


    #print('\t' * depth, '#---------------------------------------------------------')
    if debug:
        if multiply != 1:
            print('\t' * depth, '#', eq)
        else:
            print('\t' * depth, '#', multiply, '*', eq)

    if eq.startswith('(') and eq.endswith(')'):
        eq = eq[1:-1]

    # p*q
    if re.match('^[-+]?[0-9]+\*[-+]?[0-9]+$', eq):
        if multiply != 1:
            pq = eq.split('*')
            coef = int(pq[0])
            #print(1, coef)
            coef = coef * multiply
            #print(2, coef)
            neweq = str(coef) + '*' + pq[1]
            #print(3, neweq)
            return neweq
        else:
            return eq

    if re.match('^[-+]?[0-9]+\*\(', eq):
        eqp = eq.split('*', 1)
        multiplier = int(eqp[0])
        subeq = eqp[1]
        eq = eval_coefficients(subeq, multiply=multiply*multiplier, depth=depth+1)
        return eq

    # ((2*((1*8)+(-1*5)))+(-1*5)) ...
    neweq = []


    '''
    children = eq.split('+', 1) 
    for child in children:
        opens = [x for x in child if x =='(']
        closes = [x for x in child if x ==')']
        if len(opens) != len(closes):
            print(child)
            import epdb; epdb.st()
    '''
    children = split_eq_on_highest_addition(eq)
    #import epdb; epdb.st()

    if debug: print('\t' * depth, 'children:', children)
    for child in children:
        if debug: print('\t' * depth, 'rec -> %s*%s' % (multiply, child))
        newchild = eval_coefficients(child, multiply=multiply, depth=depth+1)
        if debug: print('\t' * depth, newchild)
        neweq.append(newchild)
        #pass

    neweq = ' + '.join(neweq)

    if len(neweq.split()) > 3:
        nps = neweq.split()
        nps = [x for x in nps if x != '+']
        consts = {}
        for np in nps:
            _np = np.split('*')
            key = _np[1]
            m = int(_np[0])
            if key not in consts:
                consts[key] = 0
            consts[key] += m

        neweq = []
        for k,v in consts.items():
            neweq.append('%s*%s' % (v, k))
        neweq = ' + '.join(neweq)
        #import epdb; epdb.st()

    return neweq


def simplify_coefficients(eq_arrays, debug=False):
    """
        eval and simplify the inverse equation
    """

    # [[1,8],'+',[[-1,15],'+',[-1,8]]]] --> '((1*8)+(-1*((1*15)+(-1*8))))'
    _eq = str(eq_arrays)
    _eq = _eq.replace(',', '')
    _eq = _eq.replace("'", '')
    _eq = _eq.replace('[', '(')
    _eq = _eq.replace(']', ')')
    _eq = _eq.replace(' + ', '+')
    _eq = _eq.replace(' ', '*')
    if debug: print('\t',_eq.replace('+', ' + '))

    # '((1*8)+(-1*((1*15)+(-1*8))))' --> "2*8 + -1*15"
    _neq = eval_coefficients(_eq)
    if debug: print('\t', _neq)

    # "2*8 + -1*15" --> [[2,8], '+', [-1, 15]]
    _req = _neq.split()
    for idr,r in enumerate(_req):
        if r == '+':
            continue
        a,b = r.split('*')
        _req[idr] = [int(a),int(b)]
    #import epdb; epdb.st()
    #print('\t', _req)
    return _req


def fast_exponentiation(b, exp, modulus, debug=False):
    # b^exp mod modulus
    # x^y mod modulus

    if debug:
        print('# fast exponentation: %s^%s mod %s ...' % (b, exp, modulus))

    x = b
    y = exp

    _p = 1
    s = x
    r = y

    while r > 0:

        ## THIS IS SLOW ...
        #if debug: print('p=len(%s) s=len(%s) r=%s' % (len(str(_p)), len(str(s)), r))
        if debug: print('p=%s s=%s r=%s' % (_p, s, r))

        if (r % 2) == 1:
            #if debug: print('compute p = p*s')
            _p = _p *s
        #if debug: print('compute s = s*s')
        s = s*s
        #if debug: print('compute r = r//2')
        r = r // 2 

    if debug: print('p is %s digits long' % len(str(_p)))
    if modulus is None:
        return _p

    final = _p % modulus
    if debug: print('p %% %s = %s' % (modulus, final))

    return final
    #return _p


def get_multiplicative_inverse(x, N, debug=False):
    """
    Compute s for (s*x mod N = 1) using the extended euclidean algo
    """

    # egcd?
    # sx - ty = 1
    if debug:
        print('# finding multiplicative inverse of ...')
        print('x=%s N=%s' % (x, N))
        print('')

    t0 = max(x, N)
    t1 = min(x, N)

    if debug: print('# finding divisors ...')
    divisors = [t0, t1]
    p = None
    while p is None or p > 0:
        p = t0 % t1
        if debug: print('%s %% %s = %s' % (t0, t1, p))
        if p > 0:
            divisors.append(p)
        t0 = t1
        t1 = p

    if debug:
        print('')
        print('# divisors ...')
        print(divisors)
        print('')

    if debug: print('# re-arranged divisors ...')
    variables = {}
    for idz,z in enumerate(divisors[::-1]):
        # z = g - h*i
        if z in [x, N]:
            break
        #print(z)
        g = divisors[::-1][idz+2]
        h = divisors[::-1][idz+1]
        Y = (g - z) // h

        if debug: print('%s == %s - %s*%s' % (z, g, Y,h))
        variables[z] = [g, (-1 * Y), h]
    if debug: print('')

    eq = None
    for k,v in variables.items():
        k = int(k)
        if debug:
            print('# replacing', k, '...')
            print('\t', k, ' == %s + %s*%s' % (v[0], v[1], v[2]))
        if eq is None:
            #eq = v
            eq = [[1, v[0]], '+', [v[1], v[2]]]
            continue

        for ide,_e in enumerate(eq):
            if _e == '+':
                continue
            if _e[-1] == k:
                eq[ide][-1] = [[1, v[0]], '+', [v[1], v[2]]]

        eq = simplify_coefficients(eq, debug=debug)

    if debug:
        print('')
        print('# simplification result ...')
        print('-' * len(str(eq)))
        print(eq)
        print('-' * len(str(eq)))
        print('')

    s = eq[0][0]
    t = eq[2][0]
    final = None

    if debug:
        print('# final coefficients ...')
        print('s=%s t=%s' % (s, t))
        print('')

    if debug: print('# test coefficients ...')
    # s*a + t*b
    for v in [s, t]:
        thisval = ((v*x) % N)
        if debug: print("%s*%s mod %s == %s" % (v, x, N, ((v*x) % N)))
        #print(output)
        if thisval == 1:
            final = v
    if debug: print('')

    if debug: print('# answer ...')
    answer = final % N
    if debug: print('multiplicative inverse of (%s mod %s) is %s' % (x, N, answer))
    if debug: print('\t%s %% %s = %s' % (final, N, answer))
    return answer



def test_get_multiplicative_inverse():
    '''
    #x = 77
    #N = 52
    #x = 34
    #N = 47
    #x = 7
    #N = 5
    x = 11
    N = 13
    expected = 25
    assert get_multiplicative_inverse(x, N) == expected
    '''

    res = get_multiplicative_inverse(*getCoPrimes()) 
    #import epdb; epdb.st()
