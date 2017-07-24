# -*- coding: utf-8 -*-
import scrapy
import logging
import random
from WFSpider import settings
from urlparse import urljoin
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from WFSpider.pipelines import MongoDBPipleline
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from WFSpider.items import (PublishTimeItem)
from progressbar import ProgressBar

'''
补爬上线日期
http://c.g.wanfangdata.com.cn/Periodical.aspx 类别列表
'''
mongo_cli = MongoDBPipleline()
target_year = settings.TARGET_YEAR


def contains_target_year(string):
    for year in target_year:
        if year in string:
            return True
    return False


class WfcoreSpider(CrawlSpider):
    name = 'WFpatch2'
    target_issues = []

    def start_requests(self):
        find_res = mongo_cli.article.find({"from_url": {"$regex": "2017"},
                                           "ol_publish_time": {"$exists": False}})
        find_res = list(find_res)
        res_num = len(find_res)
        find_res = random.sample(find_res, res_num)
        with ProgressBar(max_value=res_num) as bar:
            for idx, art_item in enumerate(find_res):
                url = art_item['from_url'][0]
                yield Request(url=url, callback=self.parse_article)
                bar.update(idx + 1)

    def parse_article(self, response):
        l = ItemLoader(item=PublishTimeItem(), response=response)
        l.add_value('from_url', response.url)
        l.add_xpath('p_time', "//tr[@id='wfpublishdate']//td/text()", MapCompose(unicode.strip))
        yield l.load_item()
