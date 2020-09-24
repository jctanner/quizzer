#!/usr/bin/env python3

from pprint import pprint
from itertools import combinations

def toString(List): 
    return ''.join(List) 
  
# Function to print permutations of string 
# This function takes three parameters: 
# 1. String 
# 2. Starting index of the string 
# 3. Ending index of the string. 
def permute(a, l, r): 
    res = []
    #print(a, l, r)
    if l == r: 
        #print(toString(a))
        #res.append(toString(a))
        res.append(a)
    else: 
        for i in range(l, r + 1): 
            a[l], a[i] = a[i], a[l] 
            res += permute(a, l + 1, r) 
            a[l], a[i] = a[i], a[l] # backtrack 

    return res

def main():
    balls = ['r1', 'r2', 'b3', 'b4', 'b5']

    '''
    #letters = 'abc'
    #letters = letters[::]
    #print(letters)
    #combos = get_combos(letters)
    allperms = permute(list(balls), 0, len(balls)-1)
    print('total permutations: %s' % len(allperms))
    _combos = [sorted(x) for x in allperms]
    _combos = sorted(_combos)
    combos = []
    for _combo in _combos:
        if _combo not in combos:
            combos.append(_combo)
    '''
    combos = [x for x in combinations(balls, 2)]

    print('total combinations: %s' % len(combos))

    allred = [x for x in combos if x[0].startswith('r') and x[1].startswith('r')]
    print('total red-only combinations: %s' % len(allred))

    import epdb; epdb.st()


if __name__ == "__main__":
    main()
