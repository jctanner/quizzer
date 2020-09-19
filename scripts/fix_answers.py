#!/usr/bin/env python3

import glob
import json
import os


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
        if not jd:
            BAD.add(jf)
        if jd.get('answer') is None or jd['answer'] == '':
            print(jf)
            BAD.add(jf)
            continue
        #print(jd['answer'])
        if isinstance(jd['answer'], int):
            continue
        if 'because' in jd['answer']:
            #jd['answer'] = jd['answer'].split('because')[0].strip()
            #changed = True
            pass

        #if ' or ' in jd['answer']:
        #    import epdb; epdb.st()

    for bad in BAD:
        with open(bad, 'r') as f:
            jdata = json.loads(f.read())
        if jdata.get('enabled') == True:
            continue

        jdata['enabled'] = False
        with open(bad, 'w') as f:
            f.write(json.dumps(jdata, indent=2, sort_keys=True))

    import epdb; epdb.st()


if __name__ == "__main__":
    main()
