#!/usr/bin/env python3

import random
from pprint import pprint

## MID
# int mid = low + ((high - low) / 2);

'''
boolean binarySearchIterative(int[] array, int key){
    int length = array.length;
    int low = 0;
    int high = length - 1;
    while(low <= high){
        int mid = (low + high) / 2;
        int current = array[mid];
        if(current == key){
            return true;
        }
        else if(current < key){
            low = mid + 1;
        }
        else{
            high = mid - 1;
        }
    }
    return false;
}
'''

MIDPOINTS = []


def binarySearchIterative(a, key):

    global MIDPOINTS
    MIDPOINTS = []

    print('SEARCHING %s with key %s' % (a, key))
    length = len(a)
    low = 0
    high = length - 1

    iteration = 1
    while (low <= high):
        print('')
        mid = int((low + high) / 2)
        MIDPOINTS.append(mid)
        current = a[mid]
        print('iteration %s current: %s' % (iteration, current))
        print('iteration %s mid: %s [%s]' % (iteration, mid, a[mid]))
        if (current == key):
            return True
        elif (current < key):
            low = mid + 1
        else:
            high = mid - 1
        #print('iteration %s current: %s' % (iteration, current))
        print('iteration %s high: %s [%s]' % (iteration, high, a[high]))
        #print('iteration %s mid-value: %s' % (iteration, a[mid]))
        print('iteration %s low: %s [%s]' % (iteration, low, a[low]))
        iteration += 1
    return False


def main():
    #vals = range(0, 20)
    #thislist = sorted([random.choice(vals) for x in range(0, 10)])
    #pprint(thislist)

    '''
    example = [45, 77, 89, 90, 94, 99, 100]
    key = 100
    print(binarySearchIterative(example, key))
    for idx,x in enumerate(example):
        print('')
        print(binarySearchIterative(example, x))
    '''

    '''
    vals = range(0, 100)
    thislist = sorted(set([random.choice(vals) for x in range(0, 8)]))
    thiskey = random.choice(thislist)
    pprint(thislist)
    print('Using key: %s' % thiskey)
    print('---------------------')
    binarySearchIterative(thislist, thiskey)
    '''

    '''
    thislist = [46, 77, 89, 90, 94, 99, 100]
    thiskey = 99
    pprint(thislist)
    print('Using key: %s' % thiskey)
    print('---------------------')
    binarySearchIterative(thislist, thiskey)
    '''
    vals = range(0, 100)
    thislist = sorted(set([random.choice(vals) for x in range(0, 8)]))
    thiskey = random.choice(thislist)
    pprint(thislist)

    print('Using key: %s' % thiskey)
    print('---------------------')
    input('press enter to reveal the answer:')

    binarySearchIterative(thislist, thiskey)
    print('')
    print('midpoints: %s' % (list(zip(MIDPOINTS, thislist))))

    #import epdb; epdb.st()

if __name__ == "__main__":
    main()
