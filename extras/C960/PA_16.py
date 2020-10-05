#!/usr/bin/env python


def get_product(values):
    result = 1
    for x in values:
        result = result * x
    return result


def get_factors(number):
    if number == 1:
        return [(1,number)]
    factors = []
    for i in range(1, number + 1):
        if number % i == 0:
            j = int(number / i)
            factors.append((i, j))
    #import epdb; epdb.st()
    return factors


def get_binary_bits(number):
    #print('gbf: %s' % number)
    bits = bin(number)
    bits = bits[2:]
    bits = [int(x) for x in bits]
    #import epdb; epdb.st()
    return bits


def get_base_2_powers(number):
    bits = get_binary_bits(number)
    vals = bits[::-1]

    rvals = []
    for idx,x in enumerate(vals):
        if x == 0:
            continue
        rvals.append('2^%s' % idx)
    #import epdb; epdb.st()

    return rvals


def get_base_2_dec(number):
    bits = get_binary_bits(number)
    vals = bits[::-1]

    rvals = []
    for idx,x in enumerate(vals):
        if x == 0:
            continue
        newval = 2**(idx)
        #print(newval)
        rvals.append(newval)
    #import epdb; epdb.st()

    return rvals


def fuzz(y, power, N, expected):

    bits = get_binary_bits(y)[::-1]
    bpow = get_base_2_powers(y)
    bdec = get_base_2_dec(y)
    vals = bdec[:]

    if len(bits) == 1:
        return

    psum = sum(bdec)
    if psum != power:
        return

    print('')

    modded = []
    for idx,x in enumerate(vals):
        modded.append(x % N)
 
    '''
    res = [x%N for x in vals]
    res = get_product(res) % N
    print(f'product of mods == {res}')
    import epdb; epdb.st()
    '''

    res = sum(vals) % N
    print(f'\tsum({vals}) % {N} == {res}')

    res = sum(modded) % N
    print(f'\tsum({modded}) % {N} == {res}')

    res = get_product(vals) % N
    print(f'\tproduct({vals}) % {N} == {res}')

    res = get_product(modded) % N
    print(f'\tproduct({modded}) % {N} == {res}')
    #import epdb; epdb.st()

    import epdb; epdb.st()


def main():

    # N = 12 = 2^2 + 2^3
    # m^2 is congruent to 51 mod 59
    # m^12 mod 59 is ... ?

    N = 59
    power = 12
    eremainder = 51
    expected = eremainder % N
    answer = 7
    print('expected: %s' % expected)

    for x in range(0, 100):
        squared = (x**2) % 59
        results = {} 
        equations1 = {}
        equations2 = {}
        if squared == expected:
            print('#' * 20)
            print(x)
            print('#' * 20)
            print('')
            print(f'\t{x}^2 mod 59 = {squared}')
            for y in range(1, 13):
                bits = get_binary_bits(y)[::-1]
                bpow = get_base_2_powers(y)
                bdec = get_base_2_dec(y)

                thisbase = x**y
                thisval = thisbase % N

                results[y] = thisval
                equations1[y] = f'{x}^{y} mod {N} = {thisval}'
                equations2[y] = f'{thisbase} mod {N} = {thisval}'

                if thisval != answer:
                    continue

                print('\n\t----------------------------------')
                print('\t%s^%s mod %s = %s' % (x,y, N, thisval)) 
                print('\t%s mod %s = %s' % (thisbase, N, thisval)) 
                keys = list(range(1, y+1))
                print('\tkeys: %s' % keys)
                print('\teqs:')
                for key in keys:
                    print('\t\t%s' % equations1[key])
                    print('\t\t%s' % equations2[key])
                    print('')
                #print('\tvals: %s' % [(z,results[z]) for z in keys])
                #print('')
                fuzz(y, power, N, expected)


                '''
                keys = list(range(1, y+1))
                if thisval != eremainder:
                    continue
                #import epdb; epdb.st()

                print('\t%s^%s mod %s = %s' % (x,y, N, thisval)) 
                print('\t%s mod %s = %s' % (thisbase, N, thisval)) 
                print('\n\t----------------------------------')
                print('')
                print('\ty: %s' % y)
                #print('\tkeys: %s' % keys)
                print('\tvals: %s' % [results[y] for z in keys])
                ysum = sum([results[z] for z in keys])
                print('\tsum: %s' % ysum)
                ymod = ysum % N
                print(f'\t{ysum} mod {N} = {ymod}')

                ysum = sum([results[y] for z in keys])
                print('\tsum: %s' % ysum)
                ymod = ysum % N
                print(f'\t{ysum} mod {N} = {ymod}')

                yprod = get_product([results[y] for z in keys])
                print('\tproduct: %s' % yprod)
                ymod = yprod % N
                print(f'\t{yprod} mod {N} = {ymod}')

                print('')
                #bits = get_binary_bits(y)[::-1]
                #bpow = get_base_2_powers(y)
                #bdec = get_base_2_dec(y)
                print('\t%s bits: %s' % (y, bits))
                print('\t%s bpow: %s' % (y, bpow))
                print('\t%s bdec: %s' % (y, bdec))

                fuzz_dec_vals(bdec, N, expected)
                '''

            print('')
            print('')
            #import epdb; epdb.st()
            #break

        #else:
        #    print('#%s' % x)
        #    for y in range(1, 13):
        #        thisval = (x**y) % 59
        #        print('#\t%s^%s mod 59 = %s' % (x,y, thisval)) 
   

if __name__ == "__main__":
    main()
