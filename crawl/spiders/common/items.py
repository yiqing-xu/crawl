# -*- coding: utf-8 -*-
# @Time    : 2020/4/22 9:37
# @Author  : xuyiqing
# @File    : items.py


from crawl.items import BaseItem, scrapy


class NpcItem(BaseItem):

    parent = scrapy.Field()
    title = scrapy.Field()
    sub_title = scrapy.Field()
    url = scrapy.Field()
    sub_url = scrapy.Field()
    text = scrapy.Field()
    content = scrapy.Field()
    html = scrapy.Field()
    index = scrapy.Field()
    classify = scrapy.Field()


class QAItem(BaseItem):

    url = scrapy.Field()
    html = scrapy.Field()
    question = scrapy.Field()
    question_desc = scrapy.Field()
    answer = scrapy.Field()
