# -*- coding: utf-8 -*-
import random
import requests
import json
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import random
from scrapy.dupefilters import RFPDupeFilter
import hashlib
import redis
import os
from scrapy.utils.url import canonicalize_url
from SinaWeibo import settings
from fake_useragent import UserAgent
import requests
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
import time
import base64

import logging

logger = logging.getLogger(__name__)


# 自己定义一个user_agent的类，继承了userAgentMiddleware
class RandomUserAgentMiddleware(object):
    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()
        # 从setting文件中读取RANDOM_UA_TYPE值
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE', 'random')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            '''Gets random UA based on the type setting (random, firefox…)'''
            return getattr(self.ua, self.ua_type)

        user_agent_random = get_ua()
        request.headers.setdefault('User-Agent', user_agent_random)  # 这样就是实现了User-Agent的随即变换


class CookiesMiddleware(object):
    def __init__(self, cookies_url):
        self.cookies_url = cookies_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            cookies_url=crawler.settings.get('COOKIES_URL')
        )

    def get_random_cookies(self):
        # 请求目标url获取随机cookies
        try:
            response = requests.get(self.cookies_url)
            response.raise_for_status()
            cookies = json.loads(response.text)
            return cookies
        except:
            print('cookies请求失败')

    def process_request(self, request, spider):
        # 使用代理池中的cookies发起请求
        cookies = self.get_random_cookies()
        if cookies:
            request.cookies = cookies


# 使用自己搭建的代理池
class ProxyMiddleware():
    def __init__(self, proxy_url):
        self.proxy_url = proxy_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            proxy_url=crawler.settings.get('PROXY_URL')
        )

    def get_random_proxy(self):
        # 请求目标url获取随机ip
        try:
            response = requests.get(self.proxy_url).json().get("proxy")
            response.raise_for_status()
            proxy = response.text
            return proxy
        except:
            print('ip请求失败')

    def process_request(self, request, spider):
        # 使用代理池中的ip发起请求
        # retry_times，当第一次请求失败时再启动代理ip。因为本机ip更稳定
        if request.meta.get('retry_times'):
            proxy = self.get_random_proxy()
            if proxy:
                uri = 'https://{proxy}'.format(proxy=proxy)
                print('正在使用代理', uri)
                request.meta['proxy'] = uri


