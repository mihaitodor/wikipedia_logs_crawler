# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from urllib.parse import urljoin
from dateutil.parser import parse, parserinfo
import logging

from wiki_logs.items import WikiLogsItem

class NoTwoDigitYearParserInfo(parserinfo):
    def convertyear(self, year, century_specified=False):
        if year < 100 and not century_specified:
            raise ValueError('Two digit years are not supported.')
        return parserinfo.convertyear(self, year, century_specified)


def parseDate(dateString, currentYear, retry=True):
    try:
        return parse(dateString, parserinfo = NoTwoDigitYearParserInfo(), default = datetime(currentYear, 1, 1)).date()
    except ValueError:
        if retry:
            corrections = {'Feburary': 'February',
                            'Marc': 'Mar',
                            '22-23 February': '22 February',
                            'before 2004-06-23': '2004-06-22'}
            for key, value in corrections.items():
                dateString = dateString.replace(key, value)

            return parseDate(dateString, currentYear, False)
        else:
            logging.warning('Could not parse date: %s %d' % (dateString, currentYear))

    return datetime(currentYear, 1, 1).date()

class WikiLogsSpiderSpider(scrapy.Spider):
    name = 'wiki_logs_spider'
    allowed_domains = ['wikitech.wikimedia.org']
    start_urls = ['https://wikitech.wikimedia.org/wiki/Server_Admin_Log']

    def parseArchives(self, currentUrl, h2):
        for li in h2.xpath('./following-sibling::ul[1]/li'):
            years = li.xpath('./text()').re('(\d+)')

            #the log entries are in descending order on each page
            #some older archives don't have the year embedded in the date
            #   and they traverse from the current year to the previous one
            if years:
                #select the second year from the range
                currentYear = years[1]
            else:
                currentYear = li.xpath('./a/text()').re_first('(\d+)')

            yield scrapy.Request(urljoin(currentUrl, li.xpath('./a/@href').extract_first()),
                                    callback=self.parse,
                                    meta = {'currentYear': currentYear, 'isArchiveLink': True})

    def parse(self, response):
        currentYear = int(response.meta.get('currentYear', datetime.now().year))
        currentMonth = 0
        for h2 in response.xpath('//div[@id="mw-content-text"]/h2'):
            h2Title = h2.xpath('./descendant-or-self::*/text()').extract_first()

            if h2Title == 'Archives':
                if not response.meta.get('isArchiveLink'):
                    for archiveCrawler in self.parseArchives(response.url, h2):
                        yield archiveCrawler
            else:
                itemDate = parseDate(h2Title, currentYear)

                if itemDate.month == 1 and currentMonth == 12:
                    currentYear -= 1
                    itemDate.replace(year = currentYear)

                currentMonth = itemDate.month

                item = WikiLogsItem()

                item['date'] = '{:%Y-%m-%d}'.format(itemDate)

                #the items are contained in the siblings of type ul (or pre or dl or...)
                #extract text from all siblings that follow the h2 elements for now
                item['items'] = []
                for sibling in h2.xpath('./following-sibling::*'):
                    #exit this loop when we encounter the next h2
                    if sibling.xpath('name()').extract_first() == 'h2':
                        break

                    for siblingChild in sibling.xpath('./node()'):
                        itemText = u' '.join(siblingChild.xpath('.//text()').extract()).strip()

                        if itemText:
                            item['items'].append(itemText)
                yield item
