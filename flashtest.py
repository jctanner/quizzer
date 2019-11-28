#!/usr/bin/env python3

# flashtest.py
#   A hack to let a WGU student iterate through ALL of the C172 flashcards
#   in random order and present a set of "similar" multiple choice answers.


# 1) click on the flashcard icon for a chapter
# 2) go into the quiz mode
# 3) Once the cards have loaded, view page-source
# 4) look for a textarea box with an ID for flash_content.
# 5) The flash_content has a jsonified array of all the questions
#     <textarea id="flash_content" class="h" style="display:none"> ...
# 6) Save just the JSON array to a file named like flashcards_chXX.json
# 7) run this script in the same directory

# NOTES:
#	- this must be used with python 3
#	- you need to pip/dnf/yum/etc install colorama


import argparse
import glob
import json
import os
import random
import sys
import time

from difflib import SequenceMatcher
from colorama import Fore
from colorama import Style


def cheap_levenshtein(a, b):
    '''Fake out a Levenshtein ratio'''
    _a = sorted(a[:])
    _b = sorted(b[:])
    return SequenceMatcher(None, _a, _b).ratio()


class FlashTester(object):
    _cards = None
    _json_files = None

    def __init__(self):
        self.load_files()

    @property
    def json_files(self):
        '''Cheap iterator for the json files'''
        if self._json_files is None:
            self._json_files = sorted(glob.glob('*.json'))
        return self._json_files

    def load_files(self):
        '''Cache the cards into a dict by filename and ID'''
        self._cards = {}
        for jf in self.json_files:
            with open(jf, 'r') as f:
                jdata = json.loads(f.read())
                for x in jdata:
                    self._cards[(jf, x['guid'])] = x

    def list(self):
        '''Print a list of the json files'''
        for jf in self.json_files:
            print(jf)

    def details(self):
        '''Print a summary of the cards'''
        total = 0
        for jf in self.json_files:
            with open(jf, 'r') as f:
                jdata = json.loads(f.read())
            print('%s - %d questions' % (jf, len(jdata)))
            total += len(jdata)
        print('%d total questions' % total)

    def cheap_levenshtein(a, b):
        _a = sorted(a[:])
        _b = sorted(b[:])


    def get_choices_for_card(self, key, total=4):
        question = self._cards[key]['title']
        answer = self._cards[key]['content']

        # trim down possible answer by the chapter
        choices = []
        for k,v in self._cards.items():
            if k[0] == key[0]:
                choices.append(v['content'])

        # examine all answers if not enough in this file
        if len(choices) < 4:
            for k,v in self._cards.items():
                if k[0] == key[0]:
                    choices.append(v['content'])

        # get the similarity of each choice to the answer
        ratios = []
        for x in choices:
            if x == answer:
                continue
            ratio = cheap_levenshtein(answer, x)
            ratios.append([ratio, x])

        # sort the ratios and return a few
        ratios = sorted(ratios, key=lambda x: x[0], reverse=True)
        return [x[1] for x in ratios[0:total+1]]

    def quiz(self, feedback=False):
        '''Run a quiz'''

        tally = []

        counter = 0

        keys = list(self._cards.keys())

        while True:

            os.system('cls' if os.name=='nt' else 'clear')
            k = random.choice(keys)
            v = self._cards[k]

            counter += 1
            #print(k)
            #print(v)
            print(Fore.GREEN)
            print(f'##############################################')
            print(f'# %s. %s' % (counter, v['title']))
            print(f'##############################################')
            print(Style.RESET_ALL)

            choices = self.get_choices_for_card(k)
            choices.append(v['content'])

            options = {}
            letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
            count = -1
            while choices:
                count += 1
                thischoice = random.choice(choices)
                choices.remove(thischoice)
                thisletter = letters[count]
                options[thisletter] = thischoice
                print('%s. %s' % (thisletter.upper(), thischoice))
                print()
            print()

            selection = input('Your answer (A/B/C/D/E/F/QUIT)? ')
            if selection:
                if selection.lower() == 'quit':
                    break

                selection = selection[0].lower()
                if options[selection] == v['content']:
                    tally.append([True, k])
                    if feedback:
                        print(Fore.GREEN)
                        print('CORRECT!!!')
                        print(Style.RESET_ALL)
                        time.sleep(1)
                else:
                    tally.append([False, k])
                    if feedback:
                        print(Fore.RED)
                        print('WRONG! - %s' % v['content'])
                        print(Style.RESET_ALL)
                        time.sleep(2)

        correct = len([x for x in tally if x[0]])
        incorrect = len(tally) - correct
        print('SCORE: %d percent - %s correct, %s incorrect.' % \
            (((float(correct) / float(len(tally))) * 100), correct, incorrect))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list-files', action='store_true')
    parser.add_argument('--list-details', action='store_true')
    parser.add_argument('--feedback', action='store_true')
    args = parser.parse_args()

    FT = FlashTester()
    if args.list_files:
        FT.list()
        sys.exit(0)
    elif args.list_details:
        FT.details()
        sys.exit(0)

    FT.quiz(feedback=args.feedback)


if __name__ == "__main__":
    main()