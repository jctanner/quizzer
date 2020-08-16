#!/usr/bin/env python

import copy
import glob
import json
import os
import time
from collections import OrderedDict
import bs4
from bs4 import BeautifulSoup
from logzero import logger
from selenium import webdriver
from selenium.webdriver.common.by import By

from pprint import pprint
from logzero import logger

#from wgu_tests import process_test
#from wgu_toc import read_toc
#from wgu_utils import clean_text
#from wgu_page_extractors import get_page_vocab
#from wgu_page_extractors import get_page_quiz_urls
#from wgu_page_extractors import get_page_learning_check


def can_eval(text):
    evaled = False
    try:
        eval(text)
        evaled = True
    except Exception as e:
        pass
    return evaled


def is_div_paragraph(soup):
    '''
    <div class="answer">
    <p>This is the last permutation, so there is no next permutation.</p>
    </div>
    '''

    '''
    answer_div = soup.find('div', {'class': 'answer'})
    if not answer_div:
        return False
    '''

    #paragraph = answer_div.find('p')
    paragraph = soup.find('p')
    if not paragraph:
        return False

    children = [x for x in paragraph.children]
    if len(children) != 1:
        return False

    return True


class ScrapeDMII:

    def __init__(self):
        self.toc = None
        self.image_coordinates = {}
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
        self.cdir = 'cache/C960'
        '''
        if os.path.exists('/mnt/c'):
            #self.chrome_driver = '/mnt/c/Users/jtanner/Downloads/chromedriver_win32_79y/chromedriver.exe'
            self.chrome_driver = '/mnt/c/Users/jtanner/Downloads/chromedriver_win32/chromedriver.exe'
        else:
            self.chrome_driver = os.path.expanduser('~/Downloads/chromedriver')
        self.driver = webdriver.Chrome(self.chrome_driver)
        '''
        #self.ff_driver = '/mnt/c/Users/jtanner/Downloads/geckodriver-v0.26.0-win64/geckodriver.exe'
        self.ff_driver = '/home/jtanner/Downloads/geckodriver/geckodriver'
        #self.ff_driver = '/mnt/c/Users/jtanner/Downloads/geckodriver-v0.26.0-win64'
        #import epdb; epdb.st()

        self.driver = webdriver.Firefox(executable_path=self.ff_driver)
        self.driver.maximize_window()

    @property
    def soup(self):
        ''' keep your soup fresh!'''
        return BeautifulSoup(self.driver.page_source, 'html.parser')

    def run(self):
        if not os.path.exists(self.cdir):
            os.makedirs(self.cdir)
        if not os.path.exists(os.path.join(self.cdir, 'questions')):
            os.makedirs(os.path.join(self.cdir, 'questions'))

        self.login()
        self.open_course()
        self.toc = self.get_toc()
        self.iterate_toc()
        #import epdb; epdb.st()

    def get_screenshot_at_coordinates(self, coordinates, filename):
        # driver.save_screenshot("screenshot.png")
        import epdb; epdb.st()

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

    def get_screenshot_by_id(self, elemid, filename):
        elem = self.driver.find_element_by_id(elemid)
        self._get_element_screenshot(elem, filename)

    def get_screenshot_by_classname(self, classname, filename):
        '''NOT SAFE IF DUPLICATES'''
        elem = self.driver.find_element_by_class_name(classname)
        self._get_element_screenshot(elem, filename)

    def _get_screenshot_by_elem_with_soup(self, elems, soup, filename):
        def strip_formatting(intext):
            intext = intext.replace('\xa0', '')
            intext = intext.replace('\n', '')
            intext = intext.replace(' ', '')
            intext = intext.strip()
            return intext

        thiselem = None
        for elem in elems:
            elemsoup = BeautifulSoup(elem.get_attribute('innerHTML'), 'html.parser')
            if elem.text == soup.text.strip():
                thiselem = elem
            elif strip_formatting(elem.text) == strip_formatting(soup.text):
                thiselem = elem
            elif strip_formatting(elemsoup.text) == strip_formatting(soup.text):
                thiselem = elem

        if not thiselem or thiselem is None:
            import epdb; epdb.st()

        return self._get_element_screenshot(thiselem, filename)

    def get_screenshot_by_classname_with_soup(self, classname, soup, filename):
        ''' find the matching element with class and text'''
        elems = self.driver.find_elements_by_class_name(classname)
        return self._get_screenshot_by_elem_with_soup(elems, soup, filename)

    def get_screenshot_by_tagname_with_soup(self, tagname, soup, filename):
        ''' find the matching element with class and text'''
        elems = self.driver.find_elements_by_tag_name(tagname)
        return self._get_screenshot_by_elem_with_soup( elems, soup, filename)

    def get_toc(self):

        cachefile = os.path.join(self.cdir, 'toc.json')
        if os.path.exists(cachefile):
            with open(cachefile, 'r') as f:
                section_urls = json.loads(f.read())

        else:
            # //*[@id="ember31"]
            # class=table-of-contents
            #soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            toc = self.soup.find('ul', {'class': 'table-of-contents-list'})
            list_items = toc.findAll('li')
            li_ids = [x.attrs['id'] for x in list_items]
            for liid in li_ids:
                xpath = '//*[@id="%s"]' % liid
                print('clicking on %s ...' % xpath)
                self.driver.find_element_by_xpath(xpath).click()
                time.sleep(2)

            #<div class="section-title-link-container">
            #<a href="/zybook/WGUC9602018/chapter/5/section/2" id="ember894" class="section-title-link ember-view">
            #soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            section_divs = self.soup.findAll('div', {'class': 'section-title-link-container'})

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

            with open(cachefile, 'w') as f:
                f.write(json.dumps(section_urls))

        # DEBUG: only allow up to chapter 3
        #section_urls = [x for x in section_urls if x[0][0] in ['1', '2', '3', '4']]

        with open(cachefile, 'w') as f:
            f.write(json.dumps(section_urls))

        #import epdb; epdb.st()
        return section_urls


    def reveal_answers(self):
        # FORCE SHOW ANSWER ON ALL QUESTIONS ...
        show_answer_buttons = self.soup.findAll('button', {'class': 'show-answer-button'})
        for sa_button in show_answer_buttons:
            try:
                xpath = '//*[@id="%s"]' % sa_button.attrs['id']
                self.driver.find_element_by_xpath(xpath).click()
                time.sleep(1)
                self.driver.find_element_by_xpath(xpath).click()
                time.sleep(1)
            except Exception as e:
                print(e)

    def expand_dropdowns(self):
        # EXPAND ALL SOLUTION DROP DOWNS ....
        solution_divs = self.soup.findAll('div', {'class': 'solution-button'})
        if solution_divs:
            for sd in solution_divs:
                sbutton = sd.find('button')
                sbutton_id = sbutton.attrs['id']
                xpath = '//*[@id="%s"]' % sbutton_id
                self.driver.find_element_by_xpath(xpath).click()
                time.sleep(1)

    def clean_question_div(self, this_question_div):
        # is there anything else around the question that can be removed?
        if not this_question_div.find('div', {'class': 'flex-row'}):
            question = this_question_div.prettify()
        else:
            flex_row = this_question_div.find('div', {'class': 'flex-row'})

            if flex_row.children:
                children = [x for x in flex_row.children]
                children = [x for x in children if x != '\n']
                children = [x.prettify() for x in children]

                newsrc = '<div>' + ''.join(children) + '</div>'
                print(newsrc)
                newsoup = BeautifulSoup(newsrc, 'html.parser')
                print(newsoup)
                #import epdb; epdb.st()
                question = newsoup.prettify()
            else:
                print('no children in flexrow')
                import epdb; epdb.st()

        return question


    def clean_choice_div(self, this_choice_div):
        '''
        <div class=zb-radio-button>
            <label>     <-- get children of this ..
                <span class=MathJax>
                <svg>
                    <g>
        '''

        def elem_to_string(elem):
            if isinstance(elem, bs4.element.Tag):
                return elem.prettify()
            elif isinstance(elem, bs4.element.NavigableString):
                return str(elem).replace('\n', '')
            else:
                import epdb; epdb.st()

        label = this_choice_div.find('label')
        children = [x for x in label.children]
        if len(children) == 1:
            #import epdb; epdb.st()
            return children[0]

        # [<class 'bs4.element.NavigableString'>, <class 'bs4.element.Tag'>]
        newdiv = '<div>' + ''.join([elem_to_string(x) for x in children]) + '</div>'
        newsoup = BeautifulSoup(newdiv, 'html.parser')
        #import epdb; epdb.st()
        return newsoup


    def scrape_activity_containers(self):
        # ITERATE THROUGH ACTIVITY CONTAINERS ...
        activity_containers = self.soup.findAll('div', {'class': 'interactive-activity-container'})
        for ac in activity_containers:
            instructions_div = ac.find('div', {'class': 'activity-instructions'})
            if instructions_div:
                instructions_div = instructions_div.prettify()

            # 1.4.3 if-else-statement
            title_div = ac.find('div', {'class': 'activity-title'})
            question_section_number = title_div.text.split(':')[0]
            question_divs = ac.findAll('div', {'class': 'question-set-question'})

            instructions_img = None
            if instructions_div:
                idiv = ac.find('div', {'class': 'activity-instructions'})
                fn = '%s-activity-instructions_div.png' % (question_section_number)
                instructions_img = fn
                if 'id' in idiv.attrs:
                    self.get_screenshot_by_id(idiv.attrs['id'], fn)
                else:
                    self.get_screenshot_by_classname_with_soup('activity-instructions', idiv, fn)

            # ITERATE THROUGH QUESTIONS ...
            for idqd,qd in enumerate(question_divs):

                qmeta = {
                    'title': title_div.text,
                    'section': question_section_number,
                    'qid': idqd,
                    'images': {
                        'instructions': instructions_img,
                        'question': None,
                        'choices': []
                    }
                }

                # input, fieldset|multiplechoice ...
                input_type = None
                answer = None
                explanation = None
                qd_xpath = '//*[@id="%s"]' % qd.attrs['id']
                choices = []
                correct_choice_index = None

                '''
                # screenshot the whole question div
                fn = '%s.%s-activity-question_div.png' % (question_section_number, idqd)
                self.get_screenshot_by_id(qd.attrs['id'], fn)
                '''

                # screenshot the question without inputs ...
                this_question_div = qd.find('div', {'class': 'question'})
                this_question_text_div = this_question_div.find('div', {'class': 'text'})
                fn = '%s.%s-activity-question.png' % (question_section_number, idqd)
                self.get_screenshot_by_classname_with_soup('text', this_question_text_div, fn)
                qmeta['images']['question'] = fn

                # check if true/false/etc radio buttons
                radio_divs = qd.findAll('div', {'class': 'zb-radio-button'})
                if radio_divs:
                    #answer = None
                    radio_ids = []
                    for rd in radio_divs:
                        if 'math' in rd.prettify().lower():
                            newrd = self.clean_choice_div(rd)
                            choices.append(newrd.prettify())
                        else:
                            newrd = self.clean_choice_div(rd)
                            if isinstance(newrd, bs4.element.Tag):
                                choices.append(newrd.text.strip())
                            else:
                                choices.append(newrd.strip())
                        radio_ids.append(rd.attrs['id'])
                    #for radio_id in radio_ids:
                    for idrd,rd in enumerate(radio_divs):
                        radio_id = rd.attrs['id']
                        xpath = '//*[@id="%s"]' % radio_id

                        radio_button = self.driver.find_element_by_xpath(xpath)
                        try:
                            radio_button.click()
                        except Exception as e:
                            print(e)
                            continue

                        # screenshot this choice ...
                        if radio_button.text.lower() not in ['true', 'false', 'yes', 'no']:
                            fn = '%s.%s-activity-choice-%s.png' % (question_section_number, idqd, idrd)
                            radio_button_soup = BeautifulSoup(radio_button.get_attribute('innerHTML'), 'html.parser')
                            radio_button_label_soup = radio_button_soup.find('label')
                            self.get_screenshot_by_tagname_with_soup('label', radio_button_label_soup, fn)
                            qmeta['images']['choices'].append(fn)
                        else:
                            qmeta['images']['choices'].append(None)

                        radio_button.find_element_by_tag_name('label').click()
                        time.sleep(2)

                        #soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                        qd = self.soup.find(id=qd.attrs['id'])
                        is_correct = qd.find('div', {'class': 'correct'})
                        if is_correct:
                            correct_choice_index = idrd
                            answer = rd.text.strip()
                            break

                #question = qd.find('div', {'class': 'question'}).prettify()
                this_question_div = qd.find('div', {'class': 'question'})
                question = this_question_div.prettify()
                if not answer:
                    answer = qd.find('div', {'class': 'answers'}).text.strip()

                explanation = None
                explanation_div = qd.find('div', {'class': 'explanation'})
                if explanation_div:
                    explanation = explanation_div.prettify()
                    fn = '%s-activity-explanation_div.png' % (question_section_number)
                    if 'id' in explanation_div.attrs:
                        self.get_screenshot_by_id(explanation_div.attrs['id'], fn)
                    else:
                        self.get_screenshot_by_classname_with_soup('explanation', explanation_div, fn)

                # remove the text input boxes ...
                if this_question_div.find('div', {'class': 'input'}):
                    this_question_div.find('div', {'class': 'input'}).decompose()
                    question = this_question_div.prettify()
                    input_type = 'input'
                elif this_question_div.find('fieldset'):
                    this_question_div.find('fieldset').decompose()
                    question = this_question_div.prettify()
                    input_type = 'fieldset'
                else:
                    import epdb; epdb.st()

                # log<mn>7</mn>
                # '2\n 4\n\n·3' vs 2^4 * 3 vs 24*3
                #if input_type == 'fieldset' and answer not in choices:
                #    import epdb; epdb.st()

                if input_type == 'input' and '=' in answer:
                    import epdb; epdb.st()

                # remove the label with 1), A., A) 1. ... etc ..
                if this_question_div.find('div', {'class': 'label'}):
                    this_question_div.find('div', {'class': 'label'}).decompose()
                    question = this_question_div.prettify()

                question = self.clean_question_div(this_question_div)

                #fn = 'questions/%s_activity_%s.json' % (question_section_number, idqd)
                fn = os.path.join(self.cdir, 'questions', '%s-activity-%s.json' % (question_section_number, idqd))
                logger.info('writing %s ...' % fn)
                with open(fn, 'w') as f:
                    jdata = {
                        'section': title_div.text,
                        'qid': idqd,
                        'input_type': input_type,
                        'instructions': instructions_div, 
                        'question': question,
                        'correct_choice_index': correct_choice_index,
                        'choices': choices,
                        'answer': answer,
                        'explanation': explanation
                    }
                    jdata['images'] = qmeta['images']
                    print(json.dumps(jdata, indent=2))
                    try:
                        f.write(json.dumps(jdata))
                    except Exception as e:
                        print(e)
                        import epdb; epdb.st()

                #import epdb; epdb.st()

    def scrape_exercise_containers(self):

        ignore = [
            '1.7.1',
            '2.4.1',
            '2.5.2',
            '2.24.1',
            '3.17.1',
            '3.17.3',
            '3.21.2',
            '4.3.1',
            '4.4.3',
            '4.5.1',
            '4.5.2',
            '4.7.1',
            '4.8.1',
            '4.8.2',
            '4.9.1',
            '4.9.2',
            '4.9.3',
            '4.9.4',
            '4.10.2',
            '4.10.4',
            '4.12.1',
            '4.16.1',
            '4.16.5',
            '4.18.2',
        ]
        ignore = []

        #if section[0].startswith('1.4'):
        exercise_divs = self.soup.findAll('div', {'class': 'exercise-content-resource'})
        if exercise_divs:
            for ed in exercise_divs:
                title_div = ed.find('div', {'class': 'static-container-title'})

                this_question_section = title_div.text.strip()
                question_section_number = this_question_section.split()[1].replace(':', '')
                instructions_div_1 = ed.find('div', {'class': 'setup'})
                instructions_div = ed.find('div', {'class': 'setup'}).prettify()

                instructions_img = None
                if instructions_div:
                    idiv = ed.find('div', {'class': 'setup'})
                    fn = '%s-exercise-instructions_div.png' % (question_section_number)
                    instructions_img = fn
                    if 'id' in idiv.attrs:
                        self.get_screenshot_by_id(idiv.attrs['id'], fn)
                    else:
                        self.get_screenshot_by_classname_with_soup('setup', idiv, fn)

                question_sets = ed.findAll('div', {'class': 'question-set-question'})
                for idqs,qs in enumerate(question_sets):

                    qmeta = {
                        'title': title_div.text,
                        'section': question_section_number,
                        'qid': idqs,
                        'images': {
                            'instructions': instructions_img,
                            'question': None,
                            'choices': []
                        }
                    }

                    # remove the label with 1), A., A) 1. ... etc ..
                    if qs.find('div', {'class': 'label'}):
                        qs.find('div', {'class': 'label'}).decompose()

                    question_div = qs.find('div', {'class': 'question'})
                    question_text_div = qs.find('div', {'class': 'text'})
                    question = self.clean_question_div(question_div)

                    fn = '%s.%s-exercise-question.png' % (question_section_number, idqs)
                    self.get_screenshot_by_classname_with_soup('text', question_text_div, fn)
                    qmeta['images']['question'] = fn
                    #import epdb; epdb.st()

                    answer_div = None
                    try:
                        answer_div = qs.find('div', {'class': 'answer'})
                    except Exception as e:
                        pass

                    answer = None
                    if answer_div:

                        print('-----------------------------------')
                        print(question_section_number)
                        print('-----------------------------------')

                        if question_section_number in ignore:
                            answer = answer_div.prettify()

                        # (1, 2, 3, 4, 5, 7, 6)
                        elif can_eval(answer_div.text.strip()):
                            answer = answer_div.text.strip()

                        elif is_div_paragraph(answer_div):
                            answer = answer_div.find('p').text.strip()

                        elif not answer_div.find('span', {'class': 'MathJax_SVG'}):
                            if '=' in answer_div.text:
                                answer = answer_div.text.strip().rstrip('.').split('=')[-1].strip()
                            elif answer_div.text.strip().isdigit():
                                try:
                                    answer = answer_div.text.strip()
                                except Exception as e:
                                    print(e)
                                    import epdb; epdb.st()
                            else:
                                print('CLEAN ME!!!')
                                answer = answer_div.prettify()
                                #import epdb; epdb.st()
                        else:
                            print('MATHJAX!!!')
                            if answer_div.find('script'):
                                answer = answer_div.find('script').text.strip()
                                print('%s == %s' % (question_section_number, answer))
                            else:
                                import epdb; epdb.st()

                    jdata = {
                        'section': title_div.text.strip(),
                        'qid': idqs,
                        'instructions': instructions_div, 
                        'input_type': None,
                        'question': question,
                        'choices': [],
                        'correct_choice_index': None,
                        'answer': answer,
                        'explanation': None
                    }
                    jdata['images'] = qmeta['images']

                    print(json.dumps(jdata, indent=2))

                    fn = os.path.join(self.cdir, 'questions', '%s-exercise-%s.json' % (question_section_number, idqs))
                    logger.info('writing %s ...' % fn)
                    try:
                        with open(fn, 'w') as f:
                            f.write(json.dumps(jdata))
                    except Exception as e:
                        print(e)
                        import epdb; epdb.st()

    def iterate_toc(self):
        for section in self.toc:

            logger.info('-------------------------------------------------------')
            logger.info(section)
            logger.info('-------------------------------------------------------')

            chapter = int(section[0].split('.')[0])
            chapter_section = int(section[0].split('.')[1].split()[0])

            if chapter < 3 or (chapter == 3 and chapter_section < 17):
                continue

            checkpattern = os.path.join(self.cdir, 'questions', str(section[0].split()[0]) + '.*.json')
            existing = glob.glob(checkpattern)

            url = self.zybook_base_url + section[1]
            logger.debug('option page: %s' % url)
            self.driver.get(url)
            time.sleep(2)

            logger.info('revealing answers ...')
            self.reveal_answers()
            logger.info('expanding dropdowns ...')
            self.expand_dropdowns()
            logger.info('scraping activities ...')
            self.scrape_activity_containers()
            logger.info('scraping exercises ...')
            self.scrape_exercise_containers()

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

    def get_page_meta(self, pagedir):
        mfile = os.path.join(pagedir, 'meta.json')
        with open(mfile, 'r') as f:
            meta = json.loads(f.read())
        return meta


def main():
    sps = ScrapeDMII()
    sps.run()


if __name__ == "__main__":
    main()
