# coding: utf-8
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from WFSpider.items import SubjectItem


class WfindexSpider(CrawlSpider):
    name = 'WFbase'
    start_urls = ['http://c.g.wanfangdata.com.cn/Periodical.aspx']

    def parse(self, response):
        base_url = 'http://c.g.wanfangdata.com.cn/%s'
        for table in response.xpath('//table'):
            l = ItemLoader(item=SubjectItem(), selector=table)
            l.add_xpath('class_name', "tr[1]/th/a/t/text()")
            l.add_value('class_url', base_url % table.xpath("tr[1]/th/a/@href").extract()[0])
            sub_class = []
            for sub in table.xpath('tr//li/a'):
                sub_res = {}
                ext1 = sub.xpath('@href').extract()
                if ext1:
                    sub_res['url'] = base_url % ext1[0]
                ext2 = sub.xpath('t/text()').extract()
                if ext2:
                    sub_res['name'] = ext2[0].split()
                if sub_res:
                    l.add_value('sub_class', sub_res)
            yield l.load_item()
