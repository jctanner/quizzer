#!/usr/bin/env python

def main():

    # N = 12 = 2^2 + 2^3
    # m^2 is congruent to 51 mod 59
    # m^12 mod 59 is ... ?

    expected = 51 % 59
    print('expected: %s' % expected)

    '''
    for x in range(0, 200):
        squared = (x**2) % 59
        cubed = (x**3) % 59
        dozened = (x**12) % 59

        if squared == expected:
            print(x)
            print('\t^2: %s' % squared)
            print('\t^3: %s' % cubed)
            print('\t^12: %s' % dozened)
            #import epdb; epdb.st()
    '''

    for x in range(0, 200):
        squared = (x**2) % 59

        if squared == expected:
            print(x)
            #print('\t%s^2 mod 59 = %s' % (x,squared))

            for y in range(1, 13):
                thisval = (x**y) % 59
                print('\t%s^%s mod 59 = %s' % (x,y, thisval)) 
    
    #import epdb; epdb.st()

if __name__ == "__main__":
    main()
