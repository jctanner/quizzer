#!/usr/bin/env python

import copy
import json
import os
import time
from collections import OrderedDict
from bs4 import BeautifulSoup
from logzero import logger
from selenium import webdriver

from pprint import pprint

from wgu_tests import process_test
from wgu_toc import read_toc
from wgu_utils import clean_text
from wgu_page_extractors import get_page_vocab
from wgu_page_extractors import get_page_quiz_urls
from wgu_page_extractors import get_page_learning_check


class ScrapePolSCI:

    def __init__(self):
        self.toc = None
        self.username = os.environ.get('WGU_USERNAME')
        self.password = os.environ.get('WGU_PASSWORD')
        self.login_url = 'https://my.wgu.edu/'
        self.base_url = 'https://wgu-nx.acrobatiq.com'
        self.course_url = 'https://lrps.wgu.edu/provision/148606362'
        #if os.path.exists('/mnt/c'):
        #    self.cdir = '/mnt/c/Users/jtanner/Downloads/wgu_polsci'
        #else:
        #    self.cdir = 'cache'
        self.cdir = 'cache'
        if os.path.exists('/mnt/c'):
            self.chrome_driver = '/mnt/c/Users/jtanner/Downloads/chromedriver_win32_79/chromedriver.exe'
        else:
            self.chrome_driver = os.path.expanduser('~/Downloads/chromedriver')
        self.driver = webdriver.Chrome(self.chrome_driver)

    def run(self):
        if not os.path.exists(self.cdir):
            os.makedirs(self.cdir)

        self.login()
        self.open_course()
        self.toc = read_toc(self, reload=False)
        self.iterate_course_pages()
        #self.run_quizes_and_tests()

    def login(self):
        self.driver.get(self.login_url)
        #time.sleep(10)
        time.sleep(2)
        #input('press any key once login page is loaded')

        un_box = self.driver.find_element_by_xpath('//*[@id="login-username"]')
        un_box.send_keys(self.username)
        pw_box = self.driver.find_element_by_xpath('//*[@id="login-password"]')
        pw_box.send_keys(self.password)
        signin = self.driver.find_element_by_xpath('/html/body/div/div[1]/div[1]/div/form[2]/div[3]/button')
        signin.click()
        time.sleep(8)
        #input('press any key once logged into the main page')

    def open_course(self):
        self.driver.get(self.course_url)
        time.sleep(4)
        #input('press any key once course material is loaded')
        try:
            self.driver.find_element_by_id('accept-cookie-policy').click()
        except Exception as e:
            logger.error(e)

    def iterate_course_pages(self):

        ds = []

        for pagenumber,paged in self.toc['pages'].items():

            unit = paged['unit']
            module = paged['module']
            title = paged['title']
            url = self.base_url + paged['url']
            pdir = os.path.join(self.cdir, '%s.%s.%s. %s' % (unit, module, pagenumber, title))
            print(pdir)
            print('\t%s' % url)

            pmeta = {
                'cache': pdir,
                'url': url,
                'unit': unit,
                'module': module,
                'title': title,
                'pagenum': pagenumber,
                'title': title,
            }

            if not os.path.exists(pdir):
                self.driver.get(url)
                time.sleep(4)

                os.makedirs(pdir)
                src = self.driver.page_source
                soup = BeautifulSoup(src, 'html.parser')

                with open(os.path.join(pdir, 'meta.json'), 'w') as f:
                    f.write(json.dumps(pmeta, indent=2, sort_keys=True))
                with open(os.path.join(pdir, 'page.html'), 'w') as f:
                    f.write(soup.prettify())
            
            if 'unit test' not in title.lower():
                page_vocab = get_page_vocab(pdir)
                if page_vocab:
                    for k,v in page_vocab.items():
                        ds.append({
                            'unit': unit,
                            'module': module,
                            'page': pagenumber,
                            'title': title,
                            'question': k,
                            'answer': v,
                        })

                page_questions = get_page_learning_check(pdir)
                if page_questions:
                    for pq in page_questions:
                        ds.append({
                            'unit': unit,
                            'module': module,
                            'page': pagenumber,
                            'title': title,
                            'question': pq['question'],
                            'answers': pq['answers'],
                            'hints': pq['hints']
                        })
                    #import epdb; epdb.st()
                
                quizes = get_page_quiz_urls(pdir)
                for quiz in quizes:
                    qquestions = process_test(
                        self,
                        self.base_url + quiz[0],
                        title=quiz[1],
                        page_meta=pmeta
                    )
                    for qquestion in qquestions:
                        ds.append({
                            'unit': unit,
                            'module': module,
                            'page': pagenumber,
                            'title': quiz[1],
                            'question': qquestion['question'],
                            'answers': qquestion['answers'],
                            'hints': qquestion['feedback']
                        })
                        #import epdb; epdb.st()
        
        tests = []
        for unit, unitd in self.toc['tests'].items():
            if not unitd.get('unit_test'):
                continue
            tests.append(unitd)
        tests = sorted(tests, key=lambda x: int(x['unit_number']))
        for testd in tests:
            pdir = os.path.join(self.cdir, '%s.%s.%s. %s' % (
                testd['unit_test'],
                0,
                0,
                testd['unit_title']
            ))
            tquestions = process_test(
                self,
                self.base_url + testd['unit_test'],
                title=testd['unit_title'],
                page_meta={
                    'cache': pdir,
                    'module': '0',
                    'pagenum':  0,
                    'unit': testd['unit_number'],
                    'url': testd['unit_test']
                }
            )
            for tq in tquestions:
                ds.append({
                    'unit': unit,
                    'module': 'test',
                    'page': 0,
                    'question': tq['question'],
                    'choices': tq['choices'],
                    'answers': tq['answers'],
                    'hints': tq['feedback']
                })
                #import epdb; epdb.st()
    
        logger.info('writing out all questions to json file')
        with open(os.path.join(self.cdir, 'questions.json'), 'w') as f:
            f.write(json.dumps(ds, indent=2, sort_keys=True))
        
        import epdb; epdb.st()

    def get_page_meta(self, pagedir):
        mfile = os.path.join(pagedir, 'meta.json')
        with open(mfile, 'r') as f:
            meta = json.loads(f.read())
        return meta


def main():
    sps = ScrapePolSCI()
    sps.run()


if __name__ == "__main__":
    main()
