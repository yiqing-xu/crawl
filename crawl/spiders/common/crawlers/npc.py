# -*- coding: utf-8 -*-
# @Time    : 2020/4/21 17:07
# @Author  : xuyiqing
# @File    : npc.py


import scrapy

from ..items import NpcItem
from ..models import NpcModel
from utils.crypto import md5


class NpcParaphraseSpider(scrapy.Spider):

    name = 'npc_laws_paraphrase'
    start_urls = ['http://www.npc.gov.cn/zgrdw/npc/flsyywd/node_1793.htm']

    mongodb_model = NpcModel

    def parse(self, response):
        hrefs = response.xpath("//ul[@class='classify']/li/a/@href").extract()
        for href in hrefs:
            url = response.urljoin(href)
            yield scrapy.Request(
                url,
                callback=self.parse_list
            )

    def parse_list(self, response):
        classify = response.xpath("//div[@class='div_topline']//font/font/text()").extract_first()
        hrefs = response.xpath("//div[@class='page_lie']//li/a/@href").extract()
        for href in hrefs:
            url = response.urljoin(href)
            yield scrapy.Request(
                url,
                callback=self.parse_content,
                meta={'classify': classify}
            )

    def parse_content(self, response):
        classify = response.meta.get('classify')
        title = response.xpath("//div[@class='div_topline']//font/font/text()").extract_first()
        hrefs = response.xpath("//div[@class='page_lie']//li/a/@href").extract()
        for index, href in enumerate(hrefs):
            url = response.urljoin(href)
            yield scrapy.Request(
                url,
                callback=self.parse_item,
                meta={"parent": md5(response.url), "title": title, "url": response.url, "index": index,
                      'classify': classify}
            )

    def parse_item(self, response):
        self.logger.info(response.url)
        parent = response.meta.get('parent')
        title = response.meta.get('title')
        url = response.meta.get('url')
        index = response.meta.get('index')
        classify = response.meta.get('classify')
        sub_title = response.xpath("//div[@class='tit']/h2/text()").extract_first()
        contents = response.xpath("//div[@id='pgcontent']/text()").extract()
        if not [i.strip() for i in contents if i.strip()]:
            contents = response.xpath("//div[@id='pgcontent']//p//text()").extract()
        content = ''.join(contents)
        text = '\n'.join([i.strip() for i in contents if i.strip()])
        html = response.text
        sub_url = response.url
        item = NpcItem()
        item['parent'] = parent
        item['title'] = title
        item['sub_title'] = sub_title
        item['content'] = content
        item['text'] = text
        item['html'] = html
        item['url'] = url
        item['sub_url'] = sub_url
        item['uid'] = md5(sub_url)
        item['index'] = index
        item['classify'] = classify
        yield item
