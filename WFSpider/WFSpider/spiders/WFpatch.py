# -*- coding: utf-8 -*-

from WFSpider import settings
from scrapy.spiders import CrawlSpider, Rule
from WFSpider.pipelines import MongoDBPipleline
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from WFSpider.items import (ArticleItem)

mongo_cli = MongoDBPipleline()
target_year = settings.TARGET_YEAR


def contains_target_year(string):
    for year in target_year:
        if year in string:
            return True
    return False


class WfcoreSpider(CrawlSpider):
    name = 'WFpatch'
    target_issues = []

    def start_requests(self):

        find_res = mongo_cli.article.find({})
        for art_item in find_res:
            if not art_item.has_key("author") or not art_item["author"]:
                url = art_item['from_url'][0]
                mongo_cli.article.delete_one(art_item)
                yield Request(url=url, callback=self.parse_article)

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

        yield l.load_item()
