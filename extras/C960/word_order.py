#!/usr/bin/env python3

from pprint import pprint

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
        res.append(toString(a))
    else: 
        for i in range(l, r + 1): 
            a[l], a[i] = a[i], a[l] 
            res += permute(a, l + 1, r) 
            a[l], a[i] = a[i], a[l] # backtrack 

    return res

def main():
    letters = 'abcdefg'
    #letters = 'abc'
    #letters = letters[::]
    #print(letters)
    #combos = get_combos(letters)
    allperms = permute(list(letters[::]), 0, len(letters)-1)
    #pprint(res)
    print('total permutations: %s' % len(allperms))
    print('total permutations with b in the middle: %s' % len([x for x in allperms if list(x)[3] == 'b']))
    cafterb = [x for x in allperms if x.index('b') > x.index('c')]
    print('total permutations with c after b: %s' % len(cafterb))
    tdef = [x for x in allperms if 'def' in x]
    print('total permutations with "def": %s' % len(tdef))

    b_or_c = sorted(set(cafterb + tdef))
    print('b or c: %s' % (len(b_or_c)))

    import epdb; epdb.st()


if __name__ == "__main__":
    main()
