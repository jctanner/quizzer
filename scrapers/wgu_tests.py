#!/usr/bin/env python

import copy
import json
import os
import time
from collections import OrderedDict
from bs4 import BeautifulSoup

from pprint import pprint
from logzero import logger

from wgu_utils import clean_text


def process_test(cls, testurl, title=None, page_meta=None):
    # set top level cache dir
    cdir = os.path.join(cls.cdir, '%s.%s.%s. %s' % (
        page_meta['unit'],
        page_meta['module'],
        page_meta['pagenum'],
        title))
    if not os.path.exists(cdir):
        os.makedirs(cdir)

    # set scores filename
    scores_file = os.path.join(cdir, 'scores.html')

    # set data filename
    results_file = os.path.join(cdir, 'test.html')

    # check for data
    if os.path.exists(scores_file) and os.path.exists(results_file):
        with open(results_file, 'r') as f:
            html = f.read()
        questions = parse_test_questions(html, cdir=cdir)
        return questions
 
    cls.driver.get(testurl)
    time.sleep(4)

    start_button = None
    try:
        start_button = cls.driver.find_element_by_name('start_assessment')
    except Exception as e:
        logger.error(e)
    
    if start_button is not None and start_button.text != 'RETAKE':
        print('YOU NEED TO COMPLETE THIS TEST FIRST!!!')
        import epdb; epdb.st()

    with open(scores_file, 'w') as f:
        f.write(cls.driver.page_source)

    try:
        scores = parse_test_scores(cls.driver.page_source)
    except Exception as e:
        scores = []
    perfect_score = None
    for score in scores:
        if score[0] == '100%':
            perfect_score = score
            break
    if not perfect_score:
        print('YOU NEED TO MAKE A 100% SCORE ON THIS!')
        import epdb; epdb.st()

    pscore_url = cls.base_url + perfect_score[1]
    cls.driver.get(pscore_url)
    time.sleep(4)

    with open(results_file, 'w') as f:
        f.write(cls.driver.page_source)

    questions = parse_test_questions(cls.driver.page_source, cdir=cdir)
    #import epdb; epdb.st()
    return questions

def parse_test_scores(html):

    soup = BeautifulSoup(html, 'html.parser')

    paneldiv = soup.find('div', {'class': 'clearfix previous-attempt-panel'})
    colnames = []
    scores = []
    for idt,trow in enumerate(paneldiv.findAll('tr')):
        if idt == 0:
            for th in trow.findAll('th'):
                colnames.append(clean_text(th.text))
            continue
        row_url = trow.find('a').attrs['href']
        for td in trow.findAll('td'):
            if td.find('span', {'class': 'current-score'}):
                thisscore = td.find('span', {'class': 'current-score'}).text
                #print(thisscore)
                #thisi = td.find('i')
                #thisiurl = thisi.attrs['data-revert-url']

                '''
                thisiurl = None
                try:
                    thisiurl = td.find('a').attrs['href']
                except Exception as e:
                    logger.error(e)
                    import epdb; epdb.st()
                    #continue
                '''
                scores.append([thisscore, row_url])
                
                #reviewurl = thisi.attrs['']
                #import epdb; epdb.st()

    pprint(scores)
    #import epdb; epdb.st()
    return scores

def parse_test_questions(html, cdir=None):

    questions = []

    soup = BeautifulSoup(html, 'html.parser')
    qpanels = soup.findAll(
        'div',
        {'class': 'panel panel-default question-panel'}
    )
    for qpanel in qpanels:
        #pprint(qpanel)
        answers = []
        choices = []
        feedback = None

        #question = qpanel.find('div', {'class': 'aiq question body'})
        qbody = qpanel.find('div', {'class': 'aiq question body'})
        qselect = qpanel.find('label', {'class': 'label-accessible'})
        qtable = qpanel.find('table', {'class': 'multiple-choice-grid multiple-choice-grid-striped multiple-choice-grid-header-rotated'})

        if qtable:
            questions = []

            # radio button table
            headers = [clean_text(x.text) for x in qtable.findAll('th')]

            for idr, row in enumerate(qtable.findAll('tr')):
                if idr == 0:
                    continue
                for idtd, td in enumerate(row.findAll('td')):
                    # first column ...
                    if td.attrs.get('scope') == 'row':
                        question = clean_text(td.text)
                        continue
                    # radio boxes
                    #pprint(td.attrs)
                    if td.find('input').attrs.get('checked') == 'checked':
                        #print('td: %s' % clean_text(td.text))
                        answer = headers[idtd]
                        questions.append({
                            'question': question,
                            'answers': [answer],
                            'choices': headers[1:],
                            'feedback': None
                        })

            #import epdb; epdb.st()

        elif qselect:
            # dropdown
            #question = qpanel.find('label', {'class': 'label-accessible'})
            question = clean_text(qselect.text)
            options = qpanel.findAll('option')
            for option in options:
                if clean_text(option.text) == '-Select-':
                    continue
                choices.append(clean_text(option.text))
                if option.attrs.get('selected') == 'selected':
                    answers.append(clean_text(option.text))
            feedback = qpanel.find('div', {'class': 'feedback note note-success'})
            feedback = clean_text(feedback.text)
        elif qbody:
            # multiple choice
            question = clean_text(qbody.text)
            print(question)
            choices = []
            answers = []
            for qchoice in qpanel.findAll('div', {'class': 'aiq question choice'}):
                #pprint(qchoice)
                choice = clean_text(qchoice.find('label').find('p').text)
                print('\t%s' % choice)
                choices.append(choice)
                qinput = qchoice.find('input')
                if qinput.attrs.get('checked') == 'checked':
                    answers.append(choice)
            print('')
            feedback = qpanel.find('div', {'class': 'feedback'})
            feedback = clean_text(feedback.text)

        questions.append({
            'question': question,
            'choices': choices,
            'answers': answers,
            'feedback': feedback
        })

    #import epdb; epdb.st()
    return questions