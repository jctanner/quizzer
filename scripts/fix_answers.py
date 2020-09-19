#!/usr/bin/env python3

import glob
import json
import os

import random
import re


def randomize_answer(a):
    newa = a
    numbers = re.findall('\d+', a)
    newnumbers = set()
    for number in numbers:
        if number in newnumbers:
            continue
        new_number = int(number) + random.choice(list(range(1, 10)))
        newnumbers.add(new_number)
        #print(f'{number} -> {new_number}')
        newa = newa.replace(number, str(new_number), 1)

    #import epdb; epdb.st()
    return newa


def main():
    dpath = os.path.join('react.quizzer.app', 'server', 'data', 'courses', 'C960_discrete_math_II')
    jfiles = glob.glob('%s/*.json' % dpath)

    BAD = set()

    for jf in jfiles:
        #print(jf)
        if not jf:
            continue
        changed = False
        with open(jf, 'r') as f:
            jd = json.loads(f.read())
        print(jd.get('input_type'))
        if not jd:
            BAD.add(jf)
        if jd.get('enabled') == False:
            continue
        if jd.get('answer') is None or jd['answer'] == '':
            #print(jf)
            BAD.add(jf)
            continue

        #print(jd['answer'])
        if isinstance(jd['answer'], int):
            continue
        if 'because' in jd['answer']:
            #jd['answer'] = jd['answer'].split('because')[0].strip()
            #changed = True
            answer = jd['answer']
            aparts = answer.split()
            #print(aparts)
            if aparts[1] == 'because':
                jd['answer'] = aparts[0]
                if not jd.get('explanation'):
                    jd['explanation'] = ' '.join(aparts)
                with open(jf, 'w') as f:
                    f.write(json.dumps(jd, indent=2, sort_keys=True))
                continue

        #if ' or ' in jd['answer']:
        #    import epdb; epdb.st()

        print(jf)
        #if 'mathjax' in jd.get('answer'):
        #    import epdb; epdb.st()

        '''
        if len(jd.get('answer', '')) > 10 :
            print(jd['answer'])
            #import epdb; epdb.st()
            continue
        '''

        if not jd.get('choices') and ('<sup>' in jd['answer'] or '<sub>' in jd['answer']):
            #print(jd['answer'])
            answer = jd['answer']
            choices = [randomize_answer(answer) for x in range(0, 3)]
            rindex = random.choice(list(range(0,3)))
            choices.insert(rindex, answer)
            jd['correct_choice_index'] = rindex
            jd['choices'] = choices[:]
            with open(jf, 'w') as f:
                f.write(json.dumps(jd, indent=2, sort_keys=True))
            continue
            #import epdb; epdb.st()

        if jd.get('correct_choice_index') and jd.get('choices') and not jd.get('input_type') == 'fieldset':
            jd['input_type'] = 'fieldset'
            with open(jf, 'w') as f:
                f.write(json.dumps(jd, indent=2, sort_keys=True))
            #import epdb; epdb.st()


    '''
    for bad in BAD:
        with open(bad, 'r') as f:
            jdata = json.loads(f.read())
        if jdata.get('enabled') == True:
            continue

        jdata['enabled'] = False
        with open(bad, 'w') as f:
            f.write(json.dumps(jdata, indent=2, sort_keys=True))
    '''
    #import epdb; epdb.st()


if __name__ == "__main__":
    main()
