#!/usr/bin/env python

import copy
import json
import os
import time
from collections import OrderedDict
from bs4 import BeautifulSoup

from pprint import pprint

from wgu_utils import clean_text
from wgu_utils import get_cached_soup


def get_page_vocab(pagedir):
    vocab = {}

    '''
    htmlfile = os.path.join(pagedir, 'page.html')
    logger.info(htmlfile)
    with open(htmlfile, 'r') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    '''
    soup = get_cached_soup(pagedir)

    entries = soup.findAll('span', {'class': 'aiq term entry'})
    for entry in entries:
        word = entry.text.strip()
        word = word.rstrip('.')
        definition = entry.attrs['data-content']
        definition = definition.replace('<p>', '')
        definition = definition.replace('</p>', '')
        definition = definition.strip()
        vocab[word] = definition
    
    return vocab


def get_page_learning_check(pagedir):
    questions = []

    '''
    htmlfile = os.path.join(pagedir, 'page.html')
    logger.info(htmlfile)
    with open(htmlfile, 'r') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    '''
    soup = get_cached_soup(pagedir)

    #if '2.1.9' not in pagedir:
    #    return {}

    assessments = soup.findAll('div', {'class': 'aiq wb_inline assessment'})
    for idq, aiq in enumerate(assessments):

        # skip self-assement questions
        caption = aiq.find('div', {'class': 'caption'})
        if caption and caption.text.strip().lower() == 'self-assess':
            continue

        # multiple questions on sequential panels ...
        #   <div class="assessment_step item active">
        #   <div class="assessment_step item">
        asteps = aiq.select('div[class^=assessment_step]')

        # multiple questions in the same panel ...
        #   <div class="aiq question question-wrapper multiple_choice">
        qwrappers = aiq.findAll('div', {'class': 'aiq question question-wrapper multiple_choice'})
        for iqw, qw in enumerate(qwrappers):
            qbody = qw.find('div', {'class': 'aiq question body'})
            #question = ' '.join([x for x in qbody.text.split() if x.isascii()])
            question = clean_text(qbody.text)
            question = question.replace('Hint, displayed below', '').strip()
            print('%s. %s. %s' % (idq, iqw, question))

            answers = []
            choices = []
            qcs = qw.findAll('div', {'class': 'aiq question choice'})
            for idc,qc in enumerate(qcs):
                qid = qc.find('input').attrs['id']
                thistxt = qc.find('label').text.strip()
                thistxt = clean_text(thistxt)
                choices.append(thistxt)
                print('     %s. [%s] %s' % (idc, qid, thistxt))

                checked = qc.find('input', {'checked': 'checked'})
                if checked:
                    answers.append(thistxt)
            print('     ANSWER: %s' % answers)

            hints = []
            hintdivs = qw.findAll('div', {'class': 'hint-node-body'})
            for hintdiv in hintdivs:
                hint = hintdiv.text.replace('Hint:', '').strip()
                hint = clean_text(hint)
                print('     HINT: %s' % hint)
                hints.append(hint)

            if not answers:           
                import epdb; epdb.st()
            
            questions.append({
                'question': question,
                'answers': answers,
                'choices': choices,
                'hints': hints
            })

    return questions


def get_page_quiz_urls(pagedir):
    soup = get_cached_soup(pagedir)
    quizes = []
    for h3 in soup.findAll('h3', {'class': 'quiz-link'}):
        url = h3.find('a').attrs['href']
        title = h3.find('a').text.strip()
        quizes.append([url, title])
    return quizes