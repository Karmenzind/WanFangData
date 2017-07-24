# -*- coding: utf-8 -*-

import logging
import random
from WFSpider import settings
from urlparse import urljoin
from scrapy.spiders import CrawlSpider, Rule
from WFSpider.pipelines import MongoDBPipleline
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from WFSpider.items import ArticleItem
from progressbar import ProgressBar

# http://c.g.wanfangdata.com.cn/Periodical.aspx 类别列表

mongo_cli = MongoDBPipleline()
target_year = settings.TARGET_YEAR
logger = logging.getLogger(__name__)


def contains_target_year(string):
    for year in target_year:
        if year in string:
            return True
    return False


class WfcoreSpider(CrawlSpider):
    name = 'WFcore'

    def start_requests(self):
        find_res = mongo_cli.journal.find({})
        find_res_list = list(find_res)
        res_num = len(find_res_list)
        find_res_list = random.sample(find_res_list, res_num)

        with ProgressBar(max_value=res_num) as bar:
            for idx, jn_idx in enumerate(find_res_list):
                jn_idx_url = jn_idx['url'][0]
                self.target_issues = []
                yield Request(jn_idx_url, callback=self.parse_index)
                bar.update(idx + 1)

    def parse_index(self, response):
        all_parsed = 1
        base_url = 'http://c.g.wanfangdata.com.cn/'
        # content_title = response.xpath('//h2[@class="Content_title_detail"]/text()').extract()[0]
        # 不直接用response.url，因为默认页不显示期数，影响长期爬取
        current_uri = response.xpath('//li[@class="current"]//a[@class="current"]/@href').extract()[0]
        current_url = urljoin(base_url, current_uri)
        if contains_target_year(current_uri):
            art_url_list = response.xpath(
                '//div[@class="Content_div_detail"]/ul/li/a[@class="qkcontent_name"]/@href').extract()
            for art_url in art_url_list:
                if not mongo_cli.article.find_one({'from_url': [art_url]}):
                    all_parsed = 0
                    yield Request(art_url, callback=self.parse_article)
            if all_parsed:
                logger.info("Marked %s as all_parsed." % current_url)
                mongo_cli.others.find_one_and_update({"_id": "crawled_issue"},
                                                     {"$addToSet": {"urls": current_url}})

        if not self.target_issues:
            all_parsed_url = mongo_cli.others.find_one({"_id": "crawled_issue"})["urls"]
            find_current_location = response.xpath(
                '//a[@class="yearSwitch"]/following-sibling::p[1]/a[@class="current"]')
            for location in find_current_location:
                loc_url = location.xpath('@href').extract()[0]
                if contains_target_year(loc_url):
                    followings = location.xpath('./following-sibling::*/@href').extract()
                    precedings = location.xpath('./preceding-sibling::*/@href').extract()
                    self.target_issues += precedings + followings
            for next_uri in self.target_issues:
                next_url = urljoin(base_url, next_uri)
                if next_url in all_parsed_url:
                    logger.info("Jumped over parsed issue: %s" % next_url)
                    continue
                logger.info("Next: %s" % next_url)
                yield Request(next_url, callback=self.parse_index)

    def parse_article(self, response):
        base_url = 'http://d.g.wanfangdata.com.cn/%s'
        l = ItemLoader(item=ArticleItem(), response=response)
        l.add_xpath('title', '//*[@id="title0"]/text()', MapCompose(unicode.strip))
        l.add_xpath('title_global', '//*[@id="title0"]/following-sibling::*/text()', MapCompose(unicode.strip))
        l.add_xpath('abstract', '//*[@id="detail_leftcontent"]/div//dd/text()', MapCompose(unicode.strip))
        l.add_xpath('author', '//*[@id="perildical_dl"]//tr/td/a[@namecard="true"]/text()', MapCompose(unicode.strip))
        l.add_xpath('author_global',
                    '//*[@id="perildical_dl"]//tr[contains(th/text(), "Author")]/td/text()',
                    MapCompose(unicode.strip))

        company_tag = u"作者单位"
        l.add_xpath('company',
                    '//*[@id="perildical_dl"]//tr/th[contains(t/text(), "%s")]/following-sibling::*/text()' % company_tag,
                    MapCompose(unicode.strip))

        l.add_xpath('journal_name', '//*[@class="nav_page"]//a[3]/text()', MapCompose(unicode.strip))
        l.add_xpath('journal_url', '//*[@class="nav_page"]//a[3]/@href')
        l.add_xpath('publish_issue', '//*[@class="nav_page"]//a[4]/text()')

        key_tag = u"关键词"
        l.add_xpath('keywords',
                    '//*[@id="perildical_dl"]//tr/th[contains(t/text(), "%s")]/following-sibling::td/a/text()' % key_tag,
                    MapCompose(unicode.strip))

        l.add_value('from_url', response.url)
        l.add_xpath('dl_url', '//a[@class="downloadft"]/@href')

        l.add_xpath('ol_publish_time', "//tr[@id='wfpublishdate']//td/text()", MapCompose(unicode.strip))

        yield l.load_item()
