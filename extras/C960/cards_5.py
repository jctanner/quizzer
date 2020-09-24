#!/usr/bin/env python3


def factorial(x):
    total = x
    while x > 1:
        x = x - 1
        #print(x)
        total = total * x
        #print(total)
    return total

def combinations(choices, count=None):
    combos = [] 
    total = int(factorial(len(choices)) / factorial(len(choices) - count))
    print('making %s total combinations' % total)

    thiscounter = 0
    for one in choices:
        for two in [x for x in choices if x not in [one]]:
            for three in [x for x in choices if x not in [one, two]]:
                for four in [x for x in choices if x not in [one, two, three]]:
                    for five in [x for x in choices if x not in [one, two, three, four]]:
                        thiscombo = [one, two, three, four, five]
                        combos.append(thiscombo)
                        #print(thiscombo)
                        thiscounter += 1
                        print('%s %s' % (total, thiscounter))


    import epdb; epdb.st()    
        


def get_cards():
    suits = ['SPADE', 'HEART', 'DIAMOND', 'CLUB']
    values = list(range(2,11)) + ['J', 'Q', 'K', 'A']

    cards = []
    for suit in suits:
        for v in values:
            card = '%s:%s' % (suit[0], v)
            cards.append(card)
    return cards


def get_all_hands(count=5):
    cards = get_cards()
    hands = combinations(cards, count=count)
    return hands    
    


def main():
    '''
    cards = get_cards()
    print(cards)
    print(len(cards))
    for suite in ['S', 'H', 'D', 'C']:
        print('%s == %s' % (suite, len([x for x in cards if x.startswith(suite)]))) 

    noclubs = [x for x in cards if not x.startswith('C')]
    print('noclubs = %s' % len(noclubs))
    '''

    #hands = get_all_hands()
    combinations(['A1', 'B2', 'C3'], count=2)


if __name__ == "__main__":
    main()
