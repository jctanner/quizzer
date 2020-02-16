#!/usr/bin/env python

import datetime
import json
import os


class SimpleDB:
    datafile = None

    def __init__(self):
        self.datafile = '.simpledb.json'

    def _get_data(self):
        if not os.path.exists(self.datafile):
            return []
        with open(self.datafile, 'r') as f:
            data = json.loads(f.read())
        if data is None:
            data = []
        return data

    def _set_data(self, data):
        with open(self.datafile, 'w') as f:
            f.write(json.dumps(data, indent=2))

    def insert(self, **kwargs):
        kwargs['date'] = datetime.datetime.now().isoformat()
        data = self._get_data()
        data.append(kwargs)
        self._set_data(data)

    def select(self, **kwargs):
        result = []
        rows = self._get_data()
        for row in rows:
            skip = False
            for k,v in kwargs.items():
                if row[k] != v:
                    skip = True
            if skip:
                continue
            result.append(row)
        return result