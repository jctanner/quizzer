#!/usr/bin/env python

import copy
import json
import os
import time
from collections import OrderedDict
from bs4 import BeautifulSoup
from logzero import logger

from pprint import pprint

from wgu_utils import clean_text

def read_toc(cls, reload=True):
    if reload:
        cls.open_course()
    cls.driver.find_element_by_class_name('aq-navigation-toggle').click()
    time.sleep(2)

    html = cls.driver.page_source
    toc = parse_toc(html)

    return toc


def parse_toc(html):
    toc = OrderedDict()
    soup = BeautifulSoup(html, 'html.parser')

    tocdiv = soup.find('div', {'id': 'table-of-contents'})
    panels = tocdiv.findAll('div', {'class': 'panel'})
    for panel in panels:
        div_heading = panel.find('div', {'class': 'panel-heading'})
        heading = clean_text(div_heading.text)
        if not heading:
            continue
        unit_url = div_heading.find('a').attrs['href']
        try:
            unit_number = heading.split()[1].replace(':', '')
        except Exception as e:
            continue
        unit_title = heading.split(':')[1].strip()
        print('UNIT %s. %s' % (unit_number, unit_title))
        toc[unit_number] = {
            'unit_url': unit_url,
            'unit_number': unit_number,
            'unit_title': unit_title,
            'unit_modules': OrderedDict(),
            'unit_test': None
        }

        panel_body = panel.find('div', {'class': 'panel-body'})
        list_items = panel_body.findAll('li')
        for li in list_items:

            module_title = None
            module_number = None
            module_url = None

            ma = li.find('a', {'class': 'module-title-link'})
            if ma is None:
                #import epdb; epdb.st()
                continue

            module_url = ma.attrs['href']
            module_title = clean_text(ma.text)
            if 'module' in module_title.lower():
                module_number = module_title.split()[1].replace(':', '')
                module_title = module_title.split(':')[1].strip()
                print('     MODULE %s. %s' % (module_number, module_title))
                #import epdb; epdb.st()
            else:
                print('     MODULE %s' % (module_title))

            if module_number:
                toc[unit_number]['unit_modules'][module_number] = {
                    'module_number': module_number,
                    'module_title': module_title,
                    'quizes': OrderedDict()
                }

            links = li.findAll('a')
            for link in links:
                href = link.attrs['href']
                info = clean_text(link.text)
                print('         link: %s' % info)
                if info.startswith('Quiz:'):
                    toc[unit_number]['unit_modules'][module_number]['quizes'][info] = href

        # look for a test
        ldlinks = list_items[-1].findAll('a')
        for ldlink in ldlinks:
            linktxt = clean_text(ldlink.text)
            href = link.attrs['href']
            if linktxt.startswith('Unit Test:'):
                toc[unit_number]['unit_test'] = href
                break

    pprint(toc)

    pages = parse_navigation_panel(soup)
    #import epdb; epdb.st()

    toc = {
        'pages': pages,
        'tests': copy.deepcopy(toc)
    }

    return toc

def parse_navigation_panel(soup):
    pages = OrderedDict()

    course_nav = soup.find('nav', {'class': 'course-navigation'})

    unit = None
    module = None

    lis = course_nav.findAll('li')
    for li in course_nav.findAll('li'):
        pagenum = None
        href = None
        ptitle = None
        try:
            titlea = li.find('a', {'class': 'item-title aq-navigation-row row'})
            print(titlea.text)
            print('\t%s' % titlea.attrs.get('href'))
            href = titlea.attrs.get('href')
            ttext = titlea.text
            if 'Page number' in ttext:
                pagenum = ttext.split('Page number')[-1].strip()
            if ttext.startswith('Unit') and ':' in ttext:
                unit = ttext.split(':')[0].replace('Unit', '').strip()
                module = 0
            if ttext.startswith('Module '):
                module = ttext.split(':')[0].replace('Module', '').strip()
            ptitle = ttext[:]
            if ':' in ptitle:
                ptitle = ptitle.split(':')[-1]
            if 'Page number' in ptitle:
                ptitle = ptitle.split('Page number')[0]
            ptitle = ptitle.strip()
        except Exception as e:
            logger.error(e)
        
        print('%s. %s. %s. %s %s' % (unit, module, pagenum, ptitle, href))
        if pagenum:
            pages[pagenum] = {
                'page_number': pagenum,
                'unit': unit,
                'module': module,
                'title': ptitle,
                'url': href
            }

    #import epdb; epdb.st()
    return pages