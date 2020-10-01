#!/usr/bin/env python

def Merge(List1, List2):
    outlist = []

    while List1 or List2:
        print('------------------------')
        print(List1)
        print(List2)
        if (List1 and not List2) or (not List1 and List2):
            if List1:
                outlist.append(List1[0])
                List1 = List1[1:]
            else:
                outlist.append(List2[0])
                List2 = List2[1:]

        if List1 and List2:
            outlist.append(List1[0])
            List1 = List1[1:]
            outlist.append(List2[0])
            List2 = List2[1:]

    return outlist


if __name__ == "__main__":
    A = [1,3,5]
    B = [2,4,6]

    step1 = Merge(B[:], A[:])
    step2 = Merge(A[:], step1)

    print('============================')
    print('Merge(B,A): %s' % step1)
    print('Merge(A, Merge(B,A)): %s' % step2)

