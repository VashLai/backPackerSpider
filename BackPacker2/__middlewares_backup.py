# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
import time

from stem import Signal
from stem.control import Controller

from stem import Signal
from stem.control import Controller


def _set_new_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='tor_password')
        controller.signal(Signal.NEWNYM)


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        _set_new_ip()
        request.meta['proxy'] = 'http://127.0.0.1:8118'
        spider.log('Proxy : %s' % request.meta['proxy'])


class RandomUseragentMiddleware(object):
    def process_request(self, request, spider):
        ua = UserAgent()
        request.headers['User-Agent'] = ua.random
