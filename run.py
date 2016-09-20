#!/usr/bin/env python

from subprocess import Popen
import codecs
from json import load, dump
from dateutil.parser import parse

#Use --nolog to supress scrapy logging output
Popen('scrapy crawl wiki_logs_spider -t json -o output/wiki_logs.json'.split()).wait()

with codecs.open('output/wiki_logs.json', 'r+', encoding='utf-8') as jsonFile:
    jsonData = load(jsonFile)

    jsonData.sort(reverse=True, key = lambda entry: parse(entry['date']))

    jsonFile.seek(0)
    jsonFile.truncate(0)

    dump(jsonData, jsonFile, ensure_ascii = False, indent = 4)
