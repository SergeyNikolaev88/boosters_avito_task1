# -*- coding: utf-8 -*-
import re
from itertools import chain

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class AvcoinsSpider(CrawlSpider):
    name = 'coins_count'

    allowed_domains = ['avito.ru']
    available_range = chain(range(1, 101), range(625, 726))
    start_urls = [r"https://www.avito.ru/moskva/kollektsionirovanie/monety?p={}".format(pn) for pn in available_range]

    css_val = 'a.item-description-title-link'
    rules = (
        Rule(LinkExtractor(restrict_css=css_val), callback='parse_item'),
    )

    def get_year(self, text):
        date_re = re.compile(r'([12]\d{3})')
        dates_list = []
        if text:
            dates_list = re.findall(date_re, text)
        year = 'unknown'
        for v in dates_list:
            if int(v) == 1000 or int(v) > 2020:
                continue
            else:
                year = v
                break
        return year

    def parse_item(self, response):
        self.logger.info('Item %s', response.url)

        title_text = response.css('span.title-info-title-text::text').extract_first()
        if not title_text:
            title_text = 'unknown'

        text_ad = response.css('div.item-description-text').css('p').extract_first()

        if not text_ad:
            text_ad = 'unknown'
        tag_re = re.compile(r'<.*?>')
        price_re = re.compile(r"\d+ ?р")
        text_ad = tag_re.sub(' ', text_ad)
        text_ad = price_re.sub(' ', text_ad.lower())

        year_text = self.get_year(text_ad)
        year_title = self.get_year(title_text)

        if year_title != 'unknown':
            year = year_title
        else:
            year = year_text

        ad_num = response.css('div.title-info-metadata-item::text').extract_first()
        ad_num_re = re.compile(r'№ (\d+)')
        if ad_num:
            search_res = re.search(ad_num_re, ad_num)
        else:
            search_res = None

        if search_res:
            ad_number = search_res.group(1)
        else:
            ad_number = 'unknown'

        yield {
            'year': year,
            'year_text': year_text,
            'year_title': year_title,
            'title_text': title_text,
            'number': ad_number,
            'descr': text_ad,
        }
