#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : xuyiqing
# @Time    : 2019/8/19 17:31
# @File    : openlaw_detail_encrypt.py
# @Software: PyCharm
import os

from lxml.html import etree

from .openlaw_list_encrypt import OpenlawListSpider
from ..models import OpenlawListModel, OpenlawDetailModel
from utils.proxy import proxies

openlaw_list_model = OpenlawListModel()
openlaw_detail_model = OpenlawDetailModel()

ctype_list = []
for casetype in ["民事", "刑事", "行政", "执行", "赔偿"]:
    for wenshutype in ["通知书", "判决书", "调解书", "裁定书", "决定书", "令"]:
        ctype = casetype + wenshutype
        ctype_list.append(ctype)


class OpenlawDetailSpider(OpenlawListSpider):

    name = "openlaw.cn.detail"
    allowed_domain = ["openlaw.cn"]

    def __init__(self, *args, **kwargs):
        super(OpenlawDetailSpider, self).__init__(*args, **kwargs)
        self.cookies = {"SESSION": "ODZiMzk3MzktZmUwNC00OWI3LThiYjUtYTQzYmQwMGYzNjJj"}
        self.page_size = 10
        self.query_params = {"status": False}

    def start_requests(self):
        while True:
            try:
                documents, pager = openlaw_list_model.search(self.query_params, page_size=self.page_size)
            except:
                documents, pager = openlaw_list_model.search(self.query_params, page_size=self.page_size)
            if len(pager['pages']) == 0:
                break
            for document in documents:
                if document["Case_number"]:
                    url = "http://openlaw.cn/print/judgement/{}".format(document["Document_id"])
                    self.get_cookies(document, url)

    def get_content(self, document, resp, url):
        import pdb
        pdb.set_trace()
        html = etree.HTML(resp.text)
        html_title = html.xpath('/html/head/title/text()')[0]
        if html_title == "OpenLaw":
            self.get_cookies(document, url)
            return
        item = dict(
            Document_id=document["Document_id"],
            html_text=resp.text
        )
        query = {"Document_id": item["Document_id"]}
        p = openlaw_detail_model.find_one_by_query(query)
        if not p:
            openlaw_detail_model.insert(item)
        text = html.xpath('//div[@id="wrapper"]//text()')
        content_text = [i.strip() for i in text if i.strip()]
        title = content_text[0]
        if title[-5:] in ctype_list:
            content_text[2] = title[-5:]
        content_str = "\n".join(content_text[1:-2])

    def get_cookies(self, document, url):
        import pdb
        pdb.set_trace()
        resp = self.parse_resptext(url, self.cookies)
        resp_html = etree.HTML(resp.text)
        html_title = resp_html.xpath('/html/head/title/text()')[0]
        if html_title == "OpenLaw":
            self.get_mixencrypt_cookies(resp)
            resp_again = self.parse_resptext(url, self.cookies)
            self.get_content(document, resp_again, url)
        elif "打印" in html_title:
            self.get_content(document, resp, url)
