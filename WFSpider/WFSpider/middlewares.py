# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random
import mysql.connector
import yaml
import logging
from WFSpider.user_agents import agents
from scrapy import signals
from WFSpider import settings

logger = logging.getLogger(__name__)

with open('./WFSpider/dbconfig.yaml') as f:
    __mysql_setting = yaml.load(f).get('mysql')


def obtain_proxy():
    config = {'raise_on_warnings': True, }
    config.update(__mysql_setting)
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    _sql = '''SELECT * FROM `local_proxies`
                WHERE failure_time = 0 
                AND need_auth = 0 
                ORDER BY create_time DESC LIMIT 100;'''
    cursor.execute(_sql)
    query_res = cursor.fetchall()
    cursor.close()
    cnx.close()
    return random.choice(query_res)


class UserAgentMiddleware(object):
    """ 换User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent
        if settings.USE_PROXY:
            proxy = obtain_proxy()['detail'].strip()
            request.meta['proxy'] = proxy
            logger.debug("Applying proxy: %s" % proxy)


class WfspiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
