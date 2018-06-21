# -*- coding: utf-8 -*-

import yaml

# Scrapy settings for WFSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'WFSpider'

SPIDER_MODULES = ['WFSpider.spiders']
NEWSPIDER_MODULE = 'WFSpider.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'WFSpider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 32

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
with open('./WFSpider/headers.yaml') as f:
    _headers = yaml.load(f)
DEFAULT_REQUEST_HEADERS = _headers

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'WFSpider.middlewares.WfspiderSpiderMiddleware': 543,
# }

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'WFSpider.pipelines.MongoDBPipleline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

DOWNLOAD_DELAY = 0
LOG_LEVEL = 'DEBUG'

RETRY_ENABLED = 1
RETRY_TIMES = 10

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs

#######################################################################
#                               CUSTOM                                #
#######################################################################

TARGET_YEAR = ['2017']
USE_PROXY = 0

# /* for fp-server */
# and don't use scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware
# at the same time
DOWNLOADER_MIDDLEWARES = {
    "WFSpider.middlewares.UserAgentMiddleware": 401,
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 300,
    'WFSpider.middlewares.FPServerMiddleware': 745,
}

# follow your real settings
FP_SERVER_URL = 'http://localhost:12345'
FP_SERVER_PROXY_ANONYMITY = 'anonymous'
# HTTPPROXY_AUTH_ENCODING = 'latin-l'
