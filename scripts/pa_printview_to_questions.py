#!/usr/bin/env python

import argparse

import copy
import glob
import json
import os
import shutil
import time
from collections import OrderedDict
import bs4
from bs4 import BeautifulSoup
from logzero import logger
from selenium import webdriver
from selenium.webdriver.common.by import By

from pprint import pprint
from logzero import logger


class PaExtractor:

    def __init__(self, filename):

        self.cdir = '/tmp/stuff'
        if not os.path.exists(self.cdir):
            os.makedirs(self.cdir)

        self.questions = []

        #self.filename = filename.replace(' ', '\ ')
        self.filename = os.path.expanduser(filename)

        self.url = f'file://{os.path.abspath(self.filename)}'
        #print(self.url)
        #import epdb; epdb.st()

        self.ff_driver = '/home/jtanner/Downloads/geckodriver/geckodriver'
        #self.driver = webdriver.Firefox(executable_path=self.ff_driver)
        self.driver = webdriver.Chrome()
        #self.driver.maximize_window()
        #self.driver.set_window_size(2000, 9000)
    
    @property
    def soup(self):
        ''' keep your soup fresh!'''
        return BeautifulSoup(self.driver.page_source, 'html.parser')

    def run(self):
        self.driver.get(self.url)
        time.sleep(10)
        #self.driver.maximize_window()
        soup = self.soup

        # div ng-repeat="question in ..."
        divs = soup.findAll('div')
        ngdivs = [x for x in divs if x.attrs.get('ng-repeat')]
        ngdivs = [x for x in ngdivs if x.attrs['ng-repeat'].startswith('question in')]
        for idn,ngdiv in enumerate(ngdivs):
            self.extract_ngdiv(idn+1, ngdiv)


    def _get_element_screenshot(self, elem, filename):
        # self.cdir = 'cache/C960'
        filedir = os.path.join(self.cdir, 'questions', 'images')
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        filepath = os.path.join(filedir, filename)
        logger.debug('writing image to %s ...' % filepath)
        try:
            with open(filepath, 'wb') as f:
                f.write(elem.screenshot_as_png)
            return True
        except Exception as e:
            print('Unable to write %s: %s' % (filepath, e))
            return False

    def extract_ngdiv(self, nid, ngdiv):

        ds = {
            'qid': nid,
            'section': '99.0.0: PA',
            'enabled': True,
            'instructions': None,
            'question': None,
            'choices': [],
            'explanation': None,
            'answer': None,
            'correct_choice_index': None,
            'input_type': 'fieldset',
            'images': {
                'question': None,
                'choices': [],
                'explanation': None,
                'answer': None
            }
        }

        #choices = ngdiv.findAll('td', {'ng-bind-html': 'option.answerChoice'})

        qblock = ngdiv.find('div', {'class': 'question-block'})
        qblock_children = list(qblock.children)
        question = qblock_children[1]

        dblocks = self.driver.find_elements_by_class_name('question-block')
        dblock = dblocks[nid-1]
        dp = dblock.find_element_by_tag_name('p')
        self.driver.switch_to_active_element()
        #time.sleep(60 - nid)
        #import epdb; epdb.st()

        self._get_element_screenshot(dp, 'PA-%s-question.png' % nid)
        ds['images']['question'] = 'PA-%s-question.png' % nid
        #time.sleep(1)
        #import epdb; epdb.st()

        if not question.find('img'):
            ds['question'] = question.prettify()
        else:
            print('QUESTION WITH IMAGE %s !!!' % nid)
            ds['question'] = question.text


        choice_trs = ngdiv.findAll('tr', {'ng-repeat': 'option in item.options'})
        for idc,ctr in enumerate(choice_trs):
            print(ctr.prettify())
            choice = ctr.find('td', {'ng-bind-html': 'option.answerChoice'})
            
            thischoice = None
            if len(list(choice.children)) == 1:
                if choice.find('img'):
                    thischoice = None
                    src = choice.find('img').attrs['src']
                    src = os.path.join(
                        os.path.dirname(self.filename),
                        src.replace('./', '', 1)
                    )
                    ext = src.split('.')[-1]
                    fn = 'PA-%s-choice-%s.%s' % (nid, idc, ext)
                    imgdir = os.path.join(self.cdir, 'questions', 'images')
                    #import epdb; epdb.st()
                    shutil.copy(src, os.path.join(imgdir, fn))
                    ds['images']['choices'].append(os.path.basename(fn))

                    img = choice.find('img')
                    if img.attrs.get('alt') == ' ':
                        thischoice = 'empty set'
                else:
                    thischoice = choice.text
            else:
                cchildren = list(choice.children)
                thischoice = ['<div>']
                for child in cchildren:
                    if hasattr(child, 'prettify'):
                        thischoice.append(child.prettify())
                    else:
                        thischoice.append(str(child))
                thischoice.append('</div>')
                thischoice = ''.join(thischoice)
                #import epdb; epdb.st()

            ds['choices'].append(thischoice)
            
            imgs = ctr.findAll('img')
            is_correct = False
            for img in imgs:
                if img.attrs.get('ng-if'):
                    if 'correct' in img.attrs['ng-if']:
                        is_correct = True
            if is_correct:
                ds['answer'] = thischoice
                ds['correct_choice_index'] = idc
            #import epdb; epdb.st()    
        
        #if nid == 53:
        #    import epdb; epdb.st()

        #import epdb; epdb.st()
        self.questions.append(ds)
        thisfn = '%s.%s-pa.json' % (
            ds['section'].split(':')[0],
            nid
        )
        qdir =os.path.join(self.cdir, 'questions')
        thisfn = os.path.join(qdir, thisfn)
        with open(thisfn, 'w') as f:
            f.write(json.dumps(ds, indent=2, sort_keys=True))
 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help="the PA printview html file")
    args = parser.parse_args()

    pe = PaExtractor(args.filename)
    pe.run()

if __name__ == "__main__":
    main()