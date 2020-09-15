#!/usr/bin/env python3

import glob
import subprocess
import json
import os
import sys


def main():
    dpath = os.path.join(
        'react.quizzer.app',
        'server',
        'data',
        'courses',
        'C960_discrete_math_II'
    )
    fn = os.path.join(dpath, 'BB.txt')
    print(fn)

    ds = []
    currentq = {}
    with open(fn, 'r') as f:
        for line in f.readlines():
            if not line.strip():
                continue
            if line.strip().startswith('#'):
                continue
            print(line)
            if line.lstrip() == line:
                if currentq:
                    ds.append(currentq)
                    currentq = {}
                currentq['section'] = line.strip()
                continue
            if currentq.get('section') and not currentq.get('question'):
                currentq['question'] = line.strip()
                continue
            if currentq.get('section') and currentq.get('question') and not currentq.get('answer'):
                currentq['answer'] = line.strip()
    if currentq:
        ds.append(currentq)

    for idx, x in enumerate(ds):
        section = x['section']
        section = section.replace('BB_', '')
        sparts = section.split('.')
        #sparts[2] = sparts[2] + '-bluebook'
        #import epdb; epdb.st()
        if len(sparts) == 4:
            qid = sparts[-1]
            x['section'] = '.'.join(sparts[:3]) + ' probability [bluebook]'
        else:
            qid = 0
            x['section'] = '.'.join(sparts) + ' probability [bluebook]'
        #x['fn'] = '%s.%s.json' % (x['section'], qid)
        x['fn'] = '%s.%s.%s-bb-%s.json' % (sparts[0], sparts[1], sparts[2], qid)
        x['qid'] = qid
        x['instructions'] = None
        x['input_type'] = 'input'
        #x['images'] = {}
        x['choices'] = []
        x['explanation'] = None

    for idx, x in enumerate(ds):
        thisfn = os.path.join(dpath, x['fn'])
        print(thisfn)
        with open(thisfn, 'w') as f:
            f.write(json.dumps(x, indent=2))
    #import epdb; epdb.st()


if __name__ == "__main__":
    main()
