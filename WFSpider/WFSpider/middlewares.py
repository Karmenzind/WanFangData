# -*- coding: utf-8 -*-

import logging
import random
from urllib.parse import urljoin

import requests
import yaml
from scrapy import signals
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.exceptions import NotConfigured
from scrapy.utils.httpobj import urlparse_cached
from six.moves.urllib.request import proxy_bypass

from WFSpider import settings
from WFSpider.user_agents import agents

logger = logging.getLogger(__name__)


class UserAgentMiddleware(object):
    """ 换User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent

        if settings.USE_PROXY:
            proxy = obtain_proxy()['detail'].strip()
            request.meta['proxy'] = proxy
            logger.debug("Applying proxy: %s" % proxy)


class FPServerMiddleware(HttpProxyMiddleware):
    """
    A middleware, based on FPServer, continuesly fetch random proxy
    and set it for each request.
    FPServer required.

    required config items: (Must/Optional)
        FP_SERVER_URL               M
        HTTPPROXY_AUTH_ENCODING     O   default: latin-l
        FP_SERVER_PROXY_ANONYMITY   O   default: random
            choices:    `transparent` `anonymous`
    """

    def __init__(self,
                 crawler,
                 auth_encoding,
                 fps_url,
                 anonymity):

        if not fps_url:
            raise NotConfigured('FP_SERVER_URL not configured')

        self.fps_api = urljoin(fps_url, '/api/proxy/')

        self.anonymity = anonymity

        self.logger = crawler.spider.logger
        self.crawler = crawler
        self.auth_encoding = auth_encoding

    def fetch_proxy(self, scheme):
        """
        Get proxy from fpserver by given scheme.

        :scheme: `str` proxy protocol
        :return:
            url, scheme
        """

        params = {
            "scheme": scheme,
            "anonymity": self.anonymity,
        }
        text = None
        try:
            req = requests.get(self.fps_api, params=params)
            text = req.text
            data = req.json()
        except:
            self.crawler.logger.exception(
                "Failed to fetch proxy: %s" % text)
        else:
            _code = data.get('code')
            _proxies = data.get('data', {}).get('detail', [])

            if (_code is not 0) or (not _proxies):
                self.logger.warning(
                    'Response of fetch_proxy: %s' % data)

                return
            proxy_info = _proxies[0]
            proxy_url = proxy_info['url']

            return self._get_proxy(proxy_url, scheme)

    @classmethod
    def from_crawler(cls, crawler):
        auth_encoding = crawler.settings.get('HTTPPROXY_AUTH_ENCODING',
                                             'latin-l')
        fps_url = crawler.settings.get('FP_SERVER_URL')
        anonymity = crawler.settings.get('FP_SERVER_PROXY_ANONYMITY')

        return cls(crawler, auth_encoding, fps_url, anonymity)

    def _set_proxy(self, request, scheme):
        _fetched = self.fetch_proxy(scheme)

        if not _fetched:
            self.logger.debug('No proxy fetched from fp-server.')

            return

        creds, proxy = _fetched
        request.meta['proxy'] = proxy
        self.logger.debug('Applied proxy: %s' % proxy)

        if creds:
            request.headers['Proxy-Authorization'] = b'Basic' + creds

    def process_request(self, request, spider):
        # ignore if proxy is already set

        if 'proxy' in request.meta:
            if request.meta['proxy'] is None:
                return

            # extract credentials if present
            creds, proxy_url = self._get_proxy(request.meta['proxy'], '')
            request.meta['proxy'] = proxy_url

            if creds and not request.headers.get('Proxy-Authorization'):
                request.headers['Proxy-Authorization'] = b'Basic ' + creds

            return

        parsed = urlparse_cached(request)
        scheme = parsed.scheme

        # 'no_proxy' is only supported by http schemes

        if scheme in ('http', 'https') and proxy_bypass(parsed.hostname):
            return

        self._set_proxy(request, scheme)
