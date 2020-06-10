# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import asyncio
from time import sleep

import pyppeteer
from selenium import webdriver
from lxml.html import etree
from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy.utils.response import response_status_message
from scrapy.downloadermiddlewares.retry import RetryMiddleware

from utils.proxy import proxyAuth, proxyServer

pyppeteer.DEBUG = False

pyppeteer_level = logging.WARNING
logging.getLogger('pyppeteer').setLevel(pyppeteer_level)
logging.getLogger('websockets.protocol').setLevel(pyppeteer_level)

pyppeteer_logger = logging.getLogger('pyppeteer')
pyppeteer_logger.setLevel(logging.WARNING)


class CrawlSpiderMiddleware(object):
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


class CrawlDownloaderMiddleware(object):
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


class CustomProxyMiddleware(object):
    """
    爬虫代理
    """
    def process_request(self, request, spider):
        request.meta["proxy"] = proxyServer
        request.headers["Proxy-Authorization"] = proxyAuth


class CustomRetryMiddleware(RetryMiddleware):
    """
    判断response的状态码，进行重试
    """
    def process_response(self, request, response, spider):
        if response.status != 200:
            sleep(1)
            reason = response_status_message(response.status)
            spider.logger.warning("重新请求，当前状态码{}".format(str(response.status)))
            return self._retry(request, reason, spider) or response  # _retry方法中有最大重试次数
        else:
            return response


class FaxinVerifyMiddleware(RetryMiddleware):
    """
    法信请求中间件，验证认证信息，进行登录逻辑
    """
    # def process_request(self, request, spider):
    #     if request.method == "GET":
    #         if not spider.cookies:
    #             return
    #     return None

    def process_response(self, request, response, spider):
        if "faxin" not in spider.name or spider.name == 'faxin_outline':
            return response
        if request.method == 'GET':
            html = etree.HTML(response.text)
            law_detail = html.xpath('//*[@id="Head1"]/title/text()')[0]
            if "您的访问频率过快，请稍后刷新！" in law_detail:
                reason = "请求过快，休息2秒"
                spider.logger.info(reason)
                sleep(3)
                return self._retry(request, reason, spider) or response
            # elif html.xpath('//*[@class="login"]//text()')[0] == "登录":
            #     reason = "未登录，重新登录"
            #     spider.logger.info(reason)
            #     sleep(3)
            #     return self._retry(request, reason, spider) or response
            else:
                return response
        else:
            return response


class PuppeteerDownloaderMiddleware(object):
    """
    pyppeteer的异步协程调用
    # """
    def __init__(self):
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(self.getbrowser())
        loop.run_until_complete(task)

    async def getbrowser(self):
        self.browser = await pyppeteer.launch()
        self.page = await self.browser.newPage()

    async def getnewpage(self):
        return await self.browser.newPage()

    def process_request(self, request, spider):
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(self.use_pypuppeteer(request))
        loop.run_until_complete(task)
        return HtmlResponse(url=request.url, body=task.result(), encoding="utf-8", request=request)

    async def use_pypuppeteer(self, request):
        await self.page.goto(request.url)
        await asyncio.sleep(2)
        content = await self.page.content()
        cookies = await self.page.cookies()
        from pprint import pprint
        pprint(cookies)
        return content

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        spider.logger.error(exception)


class SeleniumDownloaderMiddleware(object):
    """
    动态网站(js)调用seleniumde的Chrome
    """
    def __init__(self):
        import os
        from crawl.settings import STATICS_DIR
        self.browser = webdriver.Chrome(executable_path=os.path.join(STATICS_DIR, "chromedriver.exe"))

    def process_request(self, request, spider):
        self.browser.get(request.url)
        return HtmlResponse(url=self.browser.current_url, body=self.browser.page_source,
                            encoding="utf-8", request=request)
