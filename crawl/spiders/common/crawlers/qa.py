# -*- coding: utf-8 -*-
# @Time    : 2020/4/29 17:58
# @Author  : xuyiqing
# @File    : qa.py
import re
import math

from urllib import parse
from copy import deepcopy
import scrapy

from ..items import QAItem
from ..models import QAModel
from utils.crypto import md5


class FindlawQASpider(scrapy.Spider):

    name = 'findlaw_qa'

    mongodb_model = QAModel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'http://s.findlaw.cn/ask/?'
        self.query_params = dict(
            m='ask',
            a='index',
            q='',
            p=1
        )
        keywords = kwargs.get('keywords')
        if not keywords:
            keywords = '涨租、退租、续租、退租、房屋租赁合同、房屋租赁、不定期租赁、' \
                        '长期租赁、短期租赁、租房、承租、商场租赁、租商场、办公楼租赁、' \
                        '场地租赁、厂房租赁、租门面房、门面房租赁、租赁商铺、商铺租赁、' \
                        '厂房租赁协议、租房补贴、出租的房屋、出租房、租的店铺、' \
                        '二手房、租房合同违约、租金、房租、租赁押金、租房押金、租房定金、' \
                        '减免租金、拖欠租金、租房合同效力、续签租赁合同'
        self.keywords = keywords.split('、')

    def start_requests(self):
        for keyword in self.keywords:
            query_params = deepcopy(self.query_params)
            query_params.update(dict(q=keyword.encode('gb2312')))
            url = self.url + parse.urlencode(query_params)
            yield scrapy.Request(
                url
            )

    def parse(self, response):
        search_number = response.css('div.serch_number::text').extract_first()
        count = re.findall(r"搜索到约(\d*)条结果", search_number)[0]
        pages = math.ceil(int(count) / 10)
        if pages > 1000:
            pages = 1000
        for page in range(1, pages + 1):
            url = re.sub(r"p=\d*", "p={}".format(page), response.url)
            yield scrapy.Request(
                url,
                callback=self.parse_list
            )

    def parse_list(self, response):
        hrefs = response.css('ul.in_list li p span.url::text').extract()
        for href in hrefs:
            yield scrapy.Request(
                href,
                callback=self.parse_item,
            )

    def parse_item(self, response):
        self.logger.info('url***{}'.format(response.url))
        item = QAItem()
        url = response.url
        question = response.xpath("//h1[@class='q-title']/text()").extract()
        question = ''.join([q.strip() for q in question if q.strip()])
        question_desc = response.xpath("//p[@class='q-detail']/text()").extract()
        question_desc = ''.join([q.strip() for q in question_desc if q.strip()])
        answer_list = response.xpath("//div[@class='answer']")
        if answer_list:
            answers = answer_list[0].xpath("./div[@class='about-text']//text()").extract()
            answer = ''.join([a.strip() for a in answers if a.strip()])
        else:
            answer = ''
        item['url'] = url
        item['uid'] = md5(url)
        item['html'] = response.text
        item['question'] = question
        item['question_desc'] = question_desc
        item['answer'] = answer
        yield item


class LawtimeQASpider(scrapy.Spider):

    name = 'lawtime_qa'

    mongodb_model = QAModel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'https://so.lawtime.cn/search/ask.php?'
        self.query_params = dict(
            m='zixun',
            a='index',
            wd='租房',
            p='1'
        )
        keywords = kwargs.get('keywords')
        if not keywords:
            keywords = '续签租赁合同、租房合同效力、租房合同违约、涨租、退租、续租、退租、房屋租赁合同、房屋租赁、不定期租赁、' \
                        '长期租赁、短期租赁、租房、承租、商场租赁、租商场、办公楼租赁、' \
                        '场地租赁、厂房租赁、租门面房、门面房租赁、租赁商铺、商铺租赁、' \
                        '厂房租赁协议、租房补贴、出租的房屋、出租房、租的店铺、' \
                        '二手房、租金、房租、租赁押金、租房押金、租房定金、' \
                        '减免租金、拖欠租金、'
        self.keywords = keywords.split('、')

    def start_requests(self):
        for keyword in self.keywords:
            query_params = deepcopy(self.query_params)
            query_params.update(dict(wd=keyword))
            url = self.url + parse.urlencode(query_params)
            yield scrapy.Request(
                url
            )

    def parse(self, response):
        number_text = response.css("p.main-i::text").extract_first()
        number_count = re.findall(r'(\d+)', number_text)
        count = int(''.join(number_count))
        max_page = math.ceil(count / 10)
        if max_page > 1000:
            max_page = 1000
        for page in range(1, max_page+1):
            url = re.sub(r"p=\d*", "p={}".format(page), response.url)
            yield scrapy.Request(
                url,
                callback=self.parse_list
            )

    def parse_list(self, response):
        hrefs = response.css("li.res-a-x a::attr(href)").extract()
        hrefs = set(hrefs)
        for href in hrefs:
            yield scrapy.Request(
                href,
                callback=self.parse_item
            )

    def parse_item(self, response):
        self.logger.info('url***{}'.format(response.url))
        item = QAItem()
        url = response.url
        question = response.xpath("//h1[@class='title']/text()").extract()
        question = ''.join([q.strip() for q in question if q.strip()])
        question_desc = response.xpath("//p[@class='content']//text()").extract()
        question_desc = ''.join([q.strip() for q in question_desc if q.strip()])
        answer_list = response.xpath("//div[@class='answer-item']")
        if answer_list:
            answers = answer_list[0].xpath(".//p[@class='answer-content']//text()").extract()
            answer = ''.join([a.strip() for a in answers if a.strip()])
        else:
            answer = ''
        item['url'] = url
        item['uid'] = md5(url)
        item['html'] = response.text
        item['question'] = question
        item['question_desc'] = question_desc
        item['answer'] = answer
        yield item


class AskSpider(scrapy.Spider):

    name = 'ask_qa'

    mongodb_model = QAModel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = 'http://www.5ask.cn/ask/search.asp?'
        self.query_params = dict(
            content='',
            p='1'
        )
        keywords = kwargs.get('keywords')
        if not keywords:
            keywords = '买卖不破租赁、租赁期限'
        self.keywords = keywords.split('、')

    def start_requests(self):
        for keyword in self.keywords:
            query_params = deepcopy(self.query_params)
            query_params.update(dict(content=keyword.encode('gb2312')))
            url = self.url + parse.urlencode(query_params)
            yield scrapy.Request(
                url
            )

    def parse(self, response):
        pass
