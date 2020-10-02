#!/usr/bin/env python

from itertools import permutations

class FSM:

    def __init__(self):
        self.state = None
    
    def transition(self, bit):

        if self.state == None:
            if bit == 'f':
                self.state = 'F'
            elif bit == 'k':
                self.state = 'K'
            elif bit == 's':
                self.state = 'S'
        
        elif self.state == 'F':
            if bit == 'k':
                self.state = 'FK'
            elif bit == 's':
                self.state = 'FS'
        
        elif self.state == 'K':
            if bit == 'f':
                self.state = 'FK'
            elif bit == 's':
                self.state = 'SK'
        
        elif self.state == 'S':
            if bit == 'f':
                self.state = 'FS'
            elif bit == 'k':
                self.state = 'SK'
        
        elif self.state == 'FK':
            if bit == 's':
                self.state = 'FSK'
        
        elif self.state == 'FS':
            if bit == 'k':
                self.state = 'FSK'
                
        elif self.state == 'SK':
            if bit == 'f':
                self.state = 'FSK'
                
        elif self.state == 'FSK':
            pass

        #print('\tstate: %s' % self.state)

    def try_input(self, data):
        self.clear()
        for x in data:
            print(x)
            self.transition(x)
            print('\tstate: %s' % self.state) 
        print('\naccepted: %s' % self.accepted)

    @property    
    def accepted(self):
        return self.state == 'FSK'

    def clear(self):
        self.state = None

    def f(self):
        self.transition('f')

    def k(self):
        self.transition('k')

    def s(self):
        self.transition('s')

    




def main():
    fsm = FSM()
    fsm.try_input('fsk')

    choices = ['f', 's', 'k']
    perms3 = [x for x in permutations(choices)]
    for pm3 in perms3:
        fsm.try_input(''.join(pm3))
    
    '''
    perms6 = [x for x in permutations(choices * 3, 6)]
    for pm6 in perms6:
        fsm.try_input(''.join(pm6))
    import epdb; epdb.st()
    '''

    bits = 'fffsss'
    fsm.try_input(bits)


if __name__ == "__main__":
    main()