# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import time

import redis
from scrapy import signals

from .client.py_cli import ProxyFetcher


class JobboleProxyMiddleware(object):

    def __init__(self, redis_host, redis_port, redis_db, redis_password):
        args = dict(host=redis_host, port=redis_port, password=redis_password, db=redis_db)
        self.scheme = 'http'
        self.success_req = 'http:success:request'
        self.cur_time = 'http:success:time'
        self.request_count = 0
        self.fetcher = ProxyFetcher(self.scheme, strategy='greedy', redis_args=args)
        self.conn = redis.StrictRedis(redis_host, redis_port, redis_db, redis_password)
        self.proxy = self.get_next_proxy()
        self.start = time.time() * 1000

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(
            redis_host=crawler.settings.get("REDIS_HOST"),
            redis_port=crawler.settings.get("REDIS_PORT"),
            redis_db=crawler.settings.get("REDIS_DB"),
            redis_password=crawler.settings.get("REDIS_PASSWORD"),
        )
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        self.start = time.time() * 1000
        self.request_count += 1
        if self.request_count == 1:
            spider.logger.info("首次启动不设代理！")
        else:
            # 对request对象加上proxy
            spider.logger.info("this is request ip:" + self.proxy)
            request.meta['proxy'] = self.proxy
        return None

    def process_response(self, request, response, spider):
        end = time.time() * 1000
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status != 200:
            self.fetcher.proxy_feedback('failure', self.proxy)
            spider.logger.info('Current ip is blocked! The proxy is {}'.format(self.proxy))
            # 对当前request换下一个代理
            self.proxy = self.get_next_proxy()
            request.meta['proxy'] = self.proxy
            return request
        else:
            spider.logger.info('Request succeeded! The proxy is {}'.format(self.proxy))
            # if you use greedy strategy, you must feedback
            self.fetcher.proxy_feedback('success', self.proxy, int(end - self.start))
            # not considering transaction
            self.conn.incr(self.success_req, 1)
            self.conn.rpush(self.cur_time, int(end / 1000))
            return response

    def process_exception(self, request, exception, spider):
        spider.logger.error('Request failed!The proxy is {}. Exception:{}'.format(self.proxy, exception))
        # it's important to feedback, otherwise you may use the bad proxy next time
        self.fetcher.proxy_feedback('failure', self.proxy)
        # 对当前request换下一个代理
        self.proxy = self.get_next_proxy()
        request.meta['proxy'] = self.proxy
        return request

    def get_next_proxy(self):
        # 获取一个可用代理
        return self.fetcher.get_proxy()

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class JobboleSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class JobboleDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
