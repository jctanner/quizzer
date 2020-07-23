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
        assert self.username
        assert self.password
        self.login_url = 'https://my.wgu.edu/'
        self.base_url = 'https://wgu-nx.acrobatiq.com'
        #self.course_url = 'https://lrps.wgu.edu/provision/148606362'
        self.course_url = 'https://my.wgu.edu/courses/course/12520006'
        #self.zybook_url = 'https://learn.zybooks.com/zybook/WGUC9602018'
        self.zybook_url = 'https://lrps.wgu.edu/provision/142483754'
        self.zybook_base_url = 'https://learn.zybooks.com'
        #if os.path.exists('/mnt/c'):
        #    self.cdir = '/mnt/c/Users/jtanner/Downloads/wgu_polsci'
        #else:
        #    self.cdir = 'cache'
        self.cdir = 'cache'
        '''
        if os.path.exists('/mnt/c'):
            #self.chrome_driver = '/mnt/c/Users/jtanner/Downloads/chromedriver_win32_79y/chromedriver.exe'
            self.chrome_driver = '/mnt/c/Users/jtanner/Downloads/chromedriver_win32/chromedriver.exe'
        else:
            self.chrome_driver = os.path.expanduser('~/Downloads/chromedriver')
        self.driver = webdriver.Chrome(self.chrome_driver)
        '''
        self.ff_driver = '/mnt/c/Users/jtanner/Downloads/geckodriver-v0.26.0-win64/geckodriver.exe'
        #self.ff_driver = '/mnt/c/Users/jtanner/Downloads/geckodriver-v0.26.0-win64'
        #import epdb; epdb.st()
        self.driver = webdriver.Firefox(executable_path=self.ff_driver)

    def run(self):
        if not os.path.exists(self.cdir):
            os.makedirs(self.cdir)

        self.login()
        self.open_course()
        #self.toc = read_toc(self, reload=False)
        #self.iterate_course_pages()

        self.toc = self.get_toc()

        self.iterate_toc()
        import epdb; epdb.st()
    
    def get_toc(self):
        # //*[@id="ember31"]
        # class=table-of-contents
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        toc = soup.find('ul', {'class': 'table-of-contents-list'})
        list_items = toc.findAll('li')
        li_ids = [x.attrs['id'] for x in list_items]
        for liid in li_ids:
            xpath = '//*[@id="%s"]' % liid
            print('clicking on %s ...' % xpath)
            self.driver.find_element_by_xpath(xpath).click()
            time.sleep(2)

        #<div class="section-title-link-container">
        #<a href="/zybook/WGUC9602018/chapter/5/section/2" id="ember894" class="section-title-link ember-view">
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        section_divs = soup.findAll('div', {'class': 'section-title-link-container'})

        section_urls = []
        for section_div in section_divs:
            try:
                # span class=section_title
                span_title = section_div.find('span', {'class': 'section-title'})
                print(span_title)
                slink = section_div.find('a', {'class': 'section-title-link'})
                print(slink)
                section_urls.append([span_title.text.strip(), slink.attrs['href']])
            except Exception as e:
                print(e)

        # DEBUG: only allow up to chapter 3
        section_urls = [x for x in section_urls if x[0][0] in ['1', '2', '3']]

        #import epdb; epdb.st()
        return section_urls

    def iterate_toc(self):
        for section in self.toc:

            # 1.14.1 true/false questions ...
            #if not section[0].startswith('2.3'):
            #    continue
            #import epdb; epdb.st()

            url = self.zybook_base_url + section[1]
            print('option page: %s' % url)
            self.driver.get(url)
            time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # FORCE SHOW ANSWER ON ALL QUESTIONS ...
            show_answer_buttons = soup.findAll('button', {'class': 'show-answer-button'})
            for sa_button in show_answer_buttons:
                try:
                    xpath = '//*[@id="%s"]' % sa_button.attrs['id']
                    self.driver.find_element_by_xpath(xpath).click()
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath).click()
                    time.sleep(1)
                except Exception as e:
                    print(e)

            # RECREATE SOUP AFTER EXPANSIONS ...
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            #import epdb; epdb.st()
            
            # EXPAND ALL SOLUTION DROP DOWNS ....
            solution_divs = soup.findAll('div', {'class': 'solution-button'})
            if solution_divs:
                for sd in solution_divs:
                    sbutton = sd.find('button')
                    sbutton_id = sbutton.attrs['id']
                    xpath = '//*[@id="%s"]' % sbutton_id
                    self.driver.find_element_by_xpath(xpath).click()
                    time.sleep(1)

            # RECREATE SOUP AFTER EXPANSIONS ...
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # ITERATOR THROUGH ACTIVITY CONTAINERS ...
            activity_containers = soup.findAll('div', {'class': 'interactive-activity-container'})
            for ac in activity_containers:
                instructions_div = ac.find('div', {'class': 'activity-instructions'})
                if instructions_div:
                    instructions_div = instructions_div.prettify()

                # 1.4.3 if-else-statement
                title_div = ac.find('div', {'class': 'activity-title'})
                question_section_number = title_div.text.split(':')[0]
                question_divs = ac.findAll('div', {'class': 'question-set-question'})

                # ITERATE THROUGH QUESTIONS ...
                for idqd,qd in enumerate(question_divs):

                    answer = None
                    qd_xpath = '//*[@id="%s"]' % qd.attrs['id']
                    choices = []

                    # check if true/false/etc radio buttons
                    radio_divs = qd.findAll('div', {'class': 'zb-radio-button'})
                    if radio_divs:
                        #answer = None
                        radio_ids = []
                        for rd in radio_divs:
                            choices.append(rd.prettify())
                            radio_ids.append(rd.attrs['id'])
                        #for radio_id in radio_ids:
                        for rd in radio_divs:
                            radio_id = rd.attrs['id']
                            xpath = '//*[@id="%s"]' % radio_id
                            #radio_button = self.driver.find_element_by_xpath(xpath)

                            '''
                            while True:
                                success = False
                                try:
                                    radio_button = self.driver.find_element_by_xpath(xpath)
                                    radio_button.click()
                                    radio_button.find_element_by_tag_name('label').click()
                                    success = True
                                except Exception as e:
                                    print(e)
                                    #import epdb; epdb.st()
                                    pass
                                if not success:
                                    print('sleep ...')
                                    time.sleep(1)
                                else:
                                    break
                            '''

                            radio_button = self.driver.find_element_by_xpath(xpath)
                            radio_button.click()
                            radio_button.find_element_by_tag_name('label').click()
                            time.sleep(2)

                            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                            #import epdb; epdb.st()
                            qd = soup.find(id=qd.attrs['id'])
                            is_correct = qd.find('div', {'class': 'correct'})
                            if is_correct:
                                answer = rd.text.strip()
                                break
                            #import epdb; epdb.st()
                            
                        #import epdb; epdb.st()

                    #question = qd.text.strip()
                    question = qd.find('div', {'class': 'question'}).prettify()
                    if not answer:
                        #import epdb; epdb.st()
                        answer = qd.find('div', {'class': 'answers'}).text.strip()
                    explanation = qd.find('div', {'class': 'explanation'}).prettify()

                    fn = 'questions/%s_activity_%s.json' % (question_section_number, idqd)
                    print('writing %s ...' % fn)
                    with open(fn, 'w') as f:
                        jdata = {
                            'section': title_div.text,
                            'qid': idqd,
                            'instructions': instructions_div, 
                            'question': question,
                            'choices': choices,
                            'answer': answer,
                            'explanation': explanation
                        }
                        try:
                            f.write(json.dumps(jdata))
                        except Exception as e:
                            print(e)
                            import epdb; epdb.st()

                    #import epdb; epdb.st()

            #if section[0].startswith('1.4'):
            exercise_divs = soup.findAll('div', {'class': 'exercise-content-resource'})
            if exercise_divs:
                for ed in exercise_divs:
                    title_div = ed.find('div', {'class': 'static-container-title'})

                    this_question_section = title_div.text.strip()
                    question_section_number = this_question_section.split()[1].replace(':', '')

                    instruction_div = ed.find('div', {'class': 'setup'}).prettify()
                    question_sets = ed.findAll('div', {'class': 'question-set-question'})
                    for idqs,qs in enumerate(question_sets):

                        question_div = qs.find('div', {'class': 'question'}).prettify()
                        answer_div = None
                        try:
                            answer_div = qs.find('div', {'class': 'answer'}).prettify()
                        except Exception as e:
                            pass

                        jdata = {
                            'section': title_div.text.strip(),
                            'qid': idqs,
                            'instructions': instructions_div, 
                            'question': question,
                            'choices': [],
                            'answer': answer_div,
                            'explanation': None
                        }

                        fn = 'questions/%s_exercise_%s.json' % (question_section_number, idqs)
                        print('writing %s ...' % fn)
                        try:
                            with open(fn, 'w') as f:
                                f.write(json.dumps(jdata))
                        except Exception as e:
                            print(e)
                            import epdb; epdb.st()
        
        #import epdb; epdb.st()

    def login(self):
        self.driver.get(self.login_url)
        #time.sleep(10)
        time.sleep(2)
        #input('press any key once login page is loaded')

        #import epdb; epdb.st()
        un_box = self.driver.find_element_by_xpath('//*[@id="login-username"]')
        print('USERNAME: %s' % self.username)
        un_box.send_keys(self.username)
        pw_box = self.driver.find_element_by_xpath('//*[@id="login-password"]')
        print('PASSWORD: %s' % self.password)
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
        self.driver.get(self.zybook_url)
        time.sleep(5)

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
