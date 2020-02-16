#!/usr/bin/env python

import copy
import csv
import datetime
import json
import os
import random
import re
import os
import uuid

from pprint import pprint

from Levenshtein import jaro_winkler

from .simpledb import SimpleDB


class Quizzer:

    courses = {}
    questions = []
    sessions = {}
    cachefile = None

    def __init__(self, datapath):
        self.db = SimpleDB()
        self.datapath = datapath
        self.load_files()
        self.fix_matrixes()
        self.fix_markdown()
        self.fix_images()
        self.fix_hints()
        #self.start_quiz()
        self.cachefile = '/tmp/wgu.cache.json'

    @property
    def empty_question(self):
        data = {
            'filename': None,
            'chapter': None,
            'section': None,
            'question': '',
            'question_markdown': '',
            'answer': None,
            'choices': [],
            'hint': '',
        }
        return data.copy()

    def load_files(self):
        datafiles = set()
        for root, dirnames, filenames in os.walk(self.datapath):
            for fn in filenames:
                datafiles.add(os.path.join(root, fn))

        datafiles = sorted(set(list(datafiles)))

        for df in datafiles:

            # handle json specially
            if df.endswith('.json'):
                path_parts = df.split('/')
                course = path_parts[1]
                if course not in self.courses:
                    self.courses[course] = {}
                
                with open(df, 'r') as f:
                    jdata = json.loads(f.read())
                
                total_added = 0
                for qs in jdata:

                    try:
                        section = int(qs['module'])
                    except ValueError as e:
                        section = 99
                    if section not in self.courses[course]:
                        self.courses[course][section] = []
                    #import epdb; epdb.st()

                    data = copy.deepcopy(self.empty_question)
                    data['course'] = course
                    if 'answer' in qs:
                        data['answer'] = qs['answer']
                    else:
                        data['answer'] = qs['answers']
                    data['choices'] = qs.get('choices', [])
                    data['filename'] = df
                    #data['hint'] = '\n'.join(qs.get('hints', []))
                    data['question'] = qs['question']
                    data['chapter'] = qs['unit']
                    data['section'] = section

                    if len(data['answer']) == 1:
                        data['answer'] = data['answer'][0]

                    if data['answer'] and data['choices']:
                        self.questions.append(data)
                        total_added += 1

                #self.randomize_choices(df)
                print('%s added out of %s' % (total_added, len(jdata)))
                continue

            # handle csv files differently ...
            elif df.endswith('.csv'):
                path_parts = df.split('/')
                course = path_parts[1]
                if course not in self.courses:
                    self.courses[course] = {}

                with open(df, 'r') as csvfile:
                    csvreader = csv.reader(csvfile)
                    for row in csvreader:
                        if row[0] == 'section':
                            continue
                        #print(row)
                        tinfo = row[0].strip('"').strip("'")
                        term = row[1]
                        definition = row[2]
                        chapter = tinfo.split('.')[0]
                        section = int(tinfo.split('.')[1])
                        try:
                            subsection = tinfo.split('.')[2]
                        except IndexError:
                            subsection = 0

                        if chapter not in self.courses[course]:
                            self.courses[course][chapter] = []

                        data = self.empty_question
                        data['filename'] = df
                        data['course'] = course
                        data['chapter'] = chapter
                        data['section'] = section
                        data['question'] = definition
                        data['answer'] = term
                
                        self.questions.append(data)

                # fill in choices
                self.randomize_choices(df)
                continue

            if not df.endswith('.txt'):
                continue

            # handle the custom text file format ...
            with open(df, 'r') as f:
                lines = f.readlines()

            if not lines:
                continue

            if '#IGNORE' in lines[0]:
                continue

            path_parts = df.split('/')
            course = path_parts[1]
            if course not in self.courses:
                self.courses[course] = {}
            chapter = path_parts[2]
            if chapter not in self.courses[course]:
                self.courses[course][chapter] = []

            section = int(path_parts[-1].split('.')[1].replace('x', '0'))

            header = ''
            choices = []
            inq = False
            inh = False
            inc = False

            data = self.empty_question
            data['filename'] = df

            for line in lines:

                # questions start with [a-z0-9]) ...
                if re.match(r'^\d\)\ ', line) or re.match(r'^\w\)\ ', line):

                    inq = True
                    inc = False

                    line = line[3:]

                    if data['question']:
                        self.questions.append(data)
                    data = self.empty_question
                    data['course'] = course
                    data['chapter'] = chapter
                    data['section'] = section
                    data['filename'] = df

                    if header:
                        data['question'] = header + line.rstrip()
                    else:
                        data['question'] = line.rstrip()

                elif inq:
                    if line.startswith('HINT:'):
                        data['hint'] += line.replace('HINT:', '').lstrip()
                        inh = True
                        inq = False

                    if line.lstrip() != line:
                        data['question'] += line

                    elif line.strip():

                        # if the choice ends with "x" then it is the right answer
                        # make sure "x" is also a possible answer
                        value = line.strip()
                        if value.endswith(' x'):
                            value = value.rstrip(' x')
                            data['answer'] = value

                        if not choices:
                            data['choices'].append(value)
                        else:
                            data['choices'] = choices[:]
                            data['answer'] = value

                elif inh:
                    data['hint'] += line

                else:

                    if line.startswith('CHOICES:'):
                        choices = []
                        inc = True
                        continue

                    elif not inc:
                        header += line

                    if inc and line.strip():
                        choices.append(line.strip())

            if data['question'] and data not in self.questions:
                self.questions.append(data)


    def randomize_choices(self, filename):
        qs = []
        for idq,question in enumerate(self.questions):
            if question['filename'] == filename:
                qs.append([idq, question])

        #all_choices = [x[1]['answer'] for x in qs]
        all_choices = []
        for x in qs:
            answer = x[1]['answer']
            if isinstance(answer, list):
                for y in answer:
                    all_choices.append(y)
            else:
                all_choices.append(answer)

        for question in qs:
            answers = question[1]['answer']
            if isinstance(answers, list):
                continue
                #import epdb; epdb.st()
            answer = question[1]['answer']
            choices = [answer, random.choice(all_choices), random.choice(all_choices)]    

            matches = []
            for ac in all_choices:
                if ac.lower() == answer.lower():
                    continue
                jw = jaro_winkler(answer, ac)
                matches.append([str(jw).lower(), str(ac).lower()])
            matches = sorted(matches, key=lambda x: x[0])
            choices.append(matches[-1][1])
            choices.append(matches[-2][1])
            self.questions[question[0]]['choices'] = choices[:]
            #import epdb; epdb.st()

    def fix_hints(self):
        for idq,question in enumerate(self.questions):
            for idc,choice in enumerate(question['choices'][:]):
                if choice.startswith('HINT:'):
                    self.questions[idq]['choices'].remove(choice)
                    self.questions[idq]['hint'] = choice.replace('HINT:', '').lstrip()

    def fix_markdown(self):
        '''convert bodies to markdown'''
        for idq,question in enumerate(self.questions):
            if question['question'].startswith('<markdown>'):
                md = question['question'][:]
                md = md.replace('<markdown>', '')
                md = md.replace('</markdown>', '')
                self.questions[idq]['question_markdown'] = md

    def _replace_matrix_with_markdown(self, body):
        matrixes = re.findall(r'<matrix>[0-9;,.\(\)\/-]+</matrix>', body)
        for matrix in matrixes:
            md = matrix[:]
            md = md.replace('<matrix>', '')
            md = md.replace('</matrix>', '')
            rows = md.split(';')
            rows = [x.split(',') for x in rows]
            cols = len(rows[0])
            md = '\n\n'
            md += '|' * (cols + 1)
            md += '\n'
            md += '|' + '---|' * (cols)
            md += '\n'
            for row in rows:
                md += '|' + '|'.join(row) + '|' + '\n'
            md += '\n'

            body = body.replace(matrix, md)
        return body

    def fix_matrixes(self):
        # <matrix>6,-5;4,6</matrix>
        for idq,qs in enumerate(self.questions):
            if '<matrix>' in qs['question']:
                body = self._replace_matrix_with_markdown(qs['question'])
                if not body.startswith('<markdown>'):
                    body = '<markdown>' + '\n' + body
                if not body.rstrip().endswith('</markdown>'):
                    body = body.rstrip() + '\n' + '</markdown>'
                self.questions[idq]['question'] = body

            for idc,choice in enumerate(qs['choices']):
                if '<matrix>' in choice:
                    self.questions[idq]['choices'][idc] =  \
                        '<markdown>' + self._replace_matrix_with_markdown(choice) + '</markdown>'

            if qs['answer'] is not None:
                if '<matrix>' in qs['answer']:
                    self.questions[idq]['answer'] =  \
                        '<markdown>' + self._replace_matrix_with_markdown(qs['answer']) + '</markdown>'

    def fix_images(self):
        '''Make the image refs html friendly'''
        for qid,question in enumerate(self.questions):
            if '<image>' not in question['question']:
                continue
            body = question['question']
            body = body.replace('<image>', '<img src="')
            body = body.replace('</image>', '">')
            #body = body.replace('.png', '')
            image = body.split('"')[1]
            #image = image.replace('.png', '').strip()
            #image = image.replace('.PNG', '').strip()
            imagedir = os.path.dirname(question['filename'])

            imagefile = image
            print(imagefile)
            imagefile = imagefile.replace('.png', '').rstrip()
            print(imagefile)
            imagefile = imagefile.replace('.PNG', '').rstrip()
            print(imagefile)
            imagefile = '/' + os.path.join('images', imagedir, 'images', imagefile + '.PNG')
            #imagefile = '/' + os.path.join('images', imagedir, 'images', image + '.PNG')
            print(imagefile)
            imagefile = imagefile.strip()
            print(imagefile)

            #if not os.path.exists(os.path.join(imagedir, 'images', image + '.PNG')):
            #    import epdb; epdb.st()
            print(imagefile)

            body = body.replace(image, imagefile) 

            if '.PNG.PNG' in body:
                import epdb; epdb.st()

            self.questions[qid]['question'] = body

    def get_session(self, coursename, chaptername, section=None, count=10):
        sessionid = str(uuid.uuid4())
        qids = []

        choices = []
        if chaptername == 'all':
            choices = self.questions
        else:
            choices = [x for x in self.questions if \
                x['course'] == coursename and \
                x['chapter'] == chaptername
            ]
            if len(choices) < count:
                count = len(choices)
        if section:
            choices = [x for x in self.questions if \
                x['course'] == coursename and \
                x['chapter'] == chaptername and \
                x['section'] == section
            ]
            if len(choices) < count:
                count = len(choices)

        if len(choices) <= count:
            qids = [self.questions.index(x) for x in choices]

        else:
            for counter in range(0, count):
                qid = None

                while qid is None or qid in qids:
                    if len(qids) >= count:
                        break

                    print('get new random question (%s possible, %s so far)' % (count, len(qids)))
                    #if len(qids) == 3:
                    #    import epdb; epdb.st()

                    #qs = random.choice(self.questions)
                    qs = random.choice(choices)
                    if len(qids) >= len(choices):
                        break
                    if qs['answer'] is None:
                        continue
                    if qs['course'] != coursename:
                        continue
                    if chaptername != 'all' and qs['chapter'] != chaptername:
                        continue
                    if section and qs['section'] != section:
                        continue
                    qid = self.questions.index(qs)

                if len(qids) >= count:
                    break
                qids.append(qid)

        qids = sorted(qids, key=lambda x: self.questions[x]['filename'])
        self.sessions[sessionid] = {
            'started': datetime.datetime.now(),
            'finished': None,
            'qids': qids[:],
            'next': qids[0],
            'answers': {}
        }

        return sessionid

    def get_next_session_qid(self, sessionid):
        if sessionid not in self.sessions:
            print(list(self.sessions.keys()))
        return self.sessions[sessionid]['next']

    def get_session_report(self, sessionid):

        session = self.sessions[sessionid]
        correct = []
        incorrect = []
        incorrect_selections = {}
        incorrect_hints = {}
        unanswered = []

        correct_files = set() 
        incorrect_files = set()

        for qid in session['qids']:
            question = self.questions[qid]
            if qid not in session['answers']:
                unanswered.append(qid)
            elif session['answers'][qid] == question['answer']:
                correct.append(qid)
            else:
                incorrect.append(qid)
                incorrect_files.add(question['filename'])
                incorrect_selections[qid] = session['answers'][qid]
                incorrect_hints[qid] = question.get('hint')
    
        data = {}
        data['total_questions'] = len(session['qids'])
        data['total_answered'] = len(list(session['answers'].keys()))
        data['total_correct'] = len(correct)
        data['total_incorrect'] = len(incorrect)
        data['score'] = (float(len(correct)) / float(data['total_questions'])) * 100
        data['questions'] = {}
        for x in session['qids']:
            data['questions'][x] = self.questions[x]
        data['incorrect'] = incorrect[:]
        data['incorrect_selections'] = incorrect_selections
        data['incorrect_hints'] = incorrect_hints

        self.set_cached_answers(correct_files, incorrect_files, correct, incorrect, incorrect_selections)

        return data

    def get_cached_answers(self):

        data = {}

        for question in self.questions:
            key = question['course'] + '-' + question['chapter']
            fn = question['filename']

            if key not in data:
                data[key] = {'byfile': {}, 'byqid': {}}

            if fn not in data[key]['byfile']:
                data[key]['byfile'][fn] = []            

        try:
            if os.path.exists(self.cachefile):
                with open(self.cachefile, 'r') as f:
                    cdata = json.loads(f.read())
                for k,v in cdata.items():
                    data[k] = v
        except Exception as e:
            print(e)

        return data

    def set_cached_answers(self, correct_files, incorrect_files, correct_qids, incorrect_qids, incorrect_selections):

        data = self.get_cached_answers()

        if correct_files or incorrect_files:

            for fn in correct_files:
                path_parts = fn.split('/')
                course = path_parts[1]
                chapter = path_parts[2]
                key = course + '-' + chapter
                if key not in data:
                    continue
                    #import epdb; epdb.st()
                if fn not in data[key]['byfile']:
                    data[key]['byfile'][fn] = []
                data[key]['byfile'][fn].append(True)

            for fn in incorrect_files:
                path_parts = fn.split('/')
                course = path_parts[1]
                chapter = path_parts[2]
                key = course + '-' + chapter
                if key not in data:
                    continue
                    #import epdb; epdb.st()
                if fn not in data[key]['byfile']:
                    data[key]['byfile'][fn] = []
                data[key]['byfile'][fn].append(False)

        elif correct_qids or incorrect_qids:

            for qid in incorrect_qids:
                thisq = self.questions[qid]
                course = thisq['course']
                chapter = thisq['chapter']
                key = course + '-' + chapter
                if qid not in data[key]['byqid']:
                    data[key]['byqid'][qid] = []
                data[key]['byqid'][qid].append(False)

            for qid in correct_qids:
                thisq = self.questions[qid]
                course = thisq['course']
                chapter = thisq['chapter']
                key = course + '-' + chapter
                if qid not in data[key]['byqid']:
                    data[key]['byqid'][qid] = []
                data[key]['byqid'][qid].append(False)

        with open(self.cachefile, 'w') as f:
            f.write(json.dumps(data))

    def get_cached_answers_report_by_chapter(self, coursename=None):

        report = {}
        sections = []

        for question in self.questions:
            if coursename and question['course'] != coursename:
                continue
            if question['course'] not in report:
                report[question['course']] = {}        
            if question['chapter'] not in report[question['course']]:
                report[question['course']][question['chapter']] = {}
            key = (question['course'], question['chapter'], question['section'])
            if key not in sections:
                sections.append(key)

        report = {}
        rows = self.db.select(course=coursename)
        for row in rows:
            if row['course'] not in report:
                report[row['course']] = {}
            if row['chapter'] not in report[row['course']]:
                report[row['course']][row['chapter']] = {}
            key = (row['course'], row['chapter'], row['section'])
            if key not in sections:
                sections.append(key)

        sections = sorted(sections)

        for _section in sections:
            course = _section[0]
            chapter = _section[1]
            section = _section[2]
            if course not in report:
                report[course] = {}
            if chapter not in report[course]:
                report[course][chapter] = {}
            if section not in report[_section[0]][_section[1]]:
                report[_section[0]][_section[1]][section] = {
                    'total': 0,
                    'correct': 0,
                    'incorrect': 0
                }

        for row in rows:
            report[row['course']][row['chapter']][row['section']]['total'] += 1
            if row['correct']:
                report[row['course']][row['chapter']][row['section']]['correct'] += 1
            else:
                report[row['course']][row['chapter']][row['section']]['incorrect'] += 1


        pprint(sections)
        pprint(report)
        return report

    def __get_cached_answers_report_by_chapter(self, coursename=None):
        ds = self.get_cached_answers().copy()
        report = {}

        for k,v in ds.items():
            course,chapter = k.split('-', 1)
            if coursename and course != coursename:
                continue
            if course not in report:
                report[course] = {}
            if chapter not in report[course]:
                report[course][chapter] = {}

            for fn, answers in v['byfile'].items():
                bn = os.path.basename(fn)
                section = bn.split('.')[1]
                if '_' in section:
                    section = section.split('_')[0]
                if section not in report[course][chapter]:
                    report[course][chapter][section] = []
                for answer in answers:
                    report[course][chapter][section].append(answer)

        # numerically sort the sections
        for course,chapters in report.items():
            for chapter, sections in chapters.items():
                section_names = list(sections.keys())
                section_names = [(x, int(x.replace('x', '0'))) for x in section_names]
                section_names = sorted(section_names, key=lambda x: x[1])

                ns = OrderedDict()
                for sn in section_names:
                    res = sections[sn[0]]
                    ns[sn[0]] = res

                report[course][chapter] = ns

        for course,chapters in report.items():
            for chapter,sections in chapters.items():
                for section, answers in sections.items():
                    _answers = answers[:]
                    total = len(_answers)
                    correct = len([x for x in _answers if x])
                    incorrect = len([x for x in _answers if not x])
                    report[course][chapter][section] = {'total': total, 'correct': correct, 'incorrect': incorrect}

        return report
        

    def get_session_selected_answer(self, sessionid, questionid):
        answer = self.sessions[sessionid]['answers'].get(questionid)
        return answer

    def set_session_answer(self, sessionid, questionid, answer):
        self.sessions[sessionid]['answers'][questionid] = answer
        question = self.questions[questionid]
        kwargs = {
            'sessionid': sessionid,
            'course': question['course'],
            'chapter': question['chapter'],
            'section': question['section'],
            'questionid': questionid,
            'choices': question['choices'],
            'correct': answer == question['answer'],
            'selected': question['answer'],
            'answer': answer
        }
        self.db.insert(**kwargs)

    def start_quiz(self, total=10):

        #import epdb; epdb.st()
        #total = len(self.questions)
        results = {
            'qids': [],
            'correct': [],
            'incorrect': [],
            'score': total,
            'total': total
        }

        for counter in range(0, total):
            counter += 1

            qid = None
            while qid is None or qid in results['qids']:
                qs = random.choice(self.questions)
                qid = self.questions.index(qs)

            os.system('clear')
            print('---------------------------------------')
            print('# %s|%s %s' % (total, counter, qs['filename']))
            print('---------------------------------------')
            print('')
            print(qs['question'])
            print('')

            answers = [x for x in zip(map(chr, range(97, 123)), qs['choices'])]
            allowed = [x[0] for x in answers]
            for answer in answers:
                print('%s) %s' % (answer[0], answer[1]))

            print('')
            print('')

            answer = None
            while True:
                answer = input('CHOICE (QUIT): ')
                if answer == 'QUIT':
                    break
                #print(answer)
                #print(allowed)
                if answer in allowed:
                    aval = [x[1] for x in answers if x[0] == answer][0]
                    if aval == qs['answer']:
                        results['correct'].append(qid)
                    else:
                        results['incorrect'].append((qid, aval))
                        results['score'] -= 1
                    break
                else:
                    print(allowed)

            if answer == 'QUIT':
                break

        os.system('clear')
        #print(results)
        score = (float(results['score']) / float(results['total']))
        score = score * 100.0
        print('SCORE: %s%%' % score)
        for inc in results['incorrect']:
            print('--------------------------------')
            qs = self.questions[inc[0]]
            print('# %s' % qs['filename'])
            print(qs['question'])
            print('')
            print('ANSWER: %s' % qs['answer'])
            print('')
            print('')
            #import epdb; epdb.st()
        #import epdb; epdb.st()
