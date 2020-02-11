#!/usr/bin/env python

import copy
import json
import os
import time
from collections import OrderedDict
from bs4 import BeautifulSoup


def clean_text(a):
    if a is None:
        return ''
    b = ' '.join([x for x in a.split() if x.isascii()])
    return b

def get_cached_soup(pagedir):
    htmlfile = os.path.join(pagedir, 'page.html')
    #logger.info(htmlfile)
    with open(htmlfile, 'r') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup