#!/usr/bin/env python

import copy
import glob
import json
import os
import time

from bs4 import BeautifulSoup
from logzero import logger


class ScrapePolSCI:

    def __init__(self):
        self.cdir = '/mnt/c/Users/jtanner/Downloads/wgu_polsci'

    def run(self):
        self.meta = self.load_meta()
        self.iterate_and_extract_pages()

    def save_meta(self):
        mfile = os.path.join(self.cdir, 'meta.json')
        with open(mfile, 'w') as f:
            f.write(json.dumps(self.meta, indent=2, sort_keys=True))

    def load_meta(self):
        meta = {}
        mfile = os.path.join(self.cdir, 'meta.json')
        try:
            with open(mfile, 'r') as f:
                meta = json.loads(f.read())
            return meta
        except Exception as e:
            logger.error(e)
        return meta

    def iterate_and_extract_pages(self):
        pagedirs = glob.glob('%s/*' % self.cdir)
        pagedirs = [x for x in pagedirs if os.path.isdir(x)]        
        pagedirs = sorted(pagedirs)

        wordcount = 1
        for pagedir in pagedirs:
            page_meta = self.get_page_meta(pagedir)
            page_vocab = self.get_page_vocab(pagedir)
            for k,v in page_vocab.items():
                print('%s. %s' % (wordcount, k))
                wordcount += 1
            page_questions = self.get_page_learning_check(pagedir)
        import epdb; epdb.st()

    def get_page_meta(self, pagedir):
        mfile = os.path.join(pagedir, 'meta.json')
        with open(mfile, 'r') as f:
            meta = json.loads(f.read())
        return meta

    def get_page_vocab(self, pagedir):
        vocab = {}

        htmlfile = os.path.join(pagedir, 'page.html')
        logger.info(htmlfile)
        with open(htmlfile, 'r') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')

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

    def get_page_learning_check(self, pagedir):
        questions = {}

        htmlfile = os.path.join(pagedir, 'page.html')
        logger.info(htmlfile)
        with open(htmlfile, 'r') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')

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
                question = ' '.join([x for x in qbody.text.split() if x.isascii()])
                question = question.replace('Hint, displayed below', '').strip()
                print('%s. %s. %s' % (idq, iqw, question))

                answer = None
                choices = []
                qcs = qw.findAll('div', {'class': 'aiq question choice'})
                for idc,qc in enumerate(qcs):
                    qid = qc.find('input').attrs['id']
                    thistxt = qc.find('label').text.strip()
                    choices.append(thistxt)
                    print('     %s. [%s] %s' % (idc, qid, thistxt))

                    checked = qc.find('input', {'checked': 'checked'})
                    if checked:
                        answer = thistxt

                hintdivs = qw.findAll('div', {'class': 'hint-node-body'})
                for hintdiv in hintdivs:
                    hint = hintdiv.text.replace('Hint:', '').strip()
                    print('     HINT: %s' % hint)
                print('     ANSWER: %s' % answer)

                if answer is None:           
                    import epdb; epdb.st()

            continue


        return questions

def main():
    sps = ScrapePolSCI()
    sps.run()

if __name__ == "__main__":
    main()
