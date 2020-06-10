#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : xuyiqing
# @Time    : 2019/8/15 9:18
# @File    : openlaw_list_encrypt.py
# @Software: PyCharm
import re
import time
import math
import datetime
from copy import deepcopy
from urllib.parse import urlencode

import requests
import execjs
from lxml.html import etree

from utils.proxy import proxies
from .openlaw_login_encrypt import OpenlawLoginSpider
from .config import OpenlawCourtIdSpider
from ..models import OpenlawListModel, OpenlawCourtGetModel

openlaw_list_model = OpenlawListModel()
openlaw_courtget_model = OpenlawCourtGetModel()


class OpenlawListSpider(OpenlawCourtIdSpider, OpenlawLoginSpider):

    name = "openlaw.cn.list"
    allowed_domain = ["openlaw.cn"]
    start_urls = ["http://openlaw.cn/login.jsp"]

    def __init__(self, *args, **kwargs):
        super(OpenlawListSpider, self).__init__(*args, **kwargs)
        self.search_url = "http://openlaw.cn/search/judgement/advanced?"
        self.cookies = {"SESSION": "MjJmNzZiZDktODM2Ni00MGQ0LWJmOWItNDlhZWMyMGFiMDZj"}
        self.page_size = self.openlaw_courtid_model.count()

    def start_requests(self):
        """进行时间和法院的组合检索条件"""
        params = deepcopy(self.params_data)
        for index, date in enumerate(self.date_list):
            params["showResults"] = "true"
            start_date = date
            end_date = self.date_list[index + 1]
            params["judgeDateBegin"] = start_date
            params["judgeDateEnd"] = end_date
            try:
                court_list, _ = self.openlaw_courtid_model.search(page_size=self.page_size)
            except:
                court_list, _ = self.openlaw_courtid_model.search(page_size=self.page_size)
            for court in court_list:
                time.sleep(3)
                params["courtId"] = court["court_id"]
                url = self.search_url + urlencode(params)
                self.decide_cookies(url, "", 1)

    def decide_cookies(self, url, resp, index):
        """判断返回的html是否进行js混淆加密"""
        if not resp:
            resp = self.parse_resptext(url, self.cookies)
        resp_html = etree.HTML(resp.text)
        html_title = resp_html.xpath('/html/head/title/text()')[0]
        if html_title == "OpenLaw":
            self.get_mixencrypt_cookies(resp)
            resp_again = self.parse_resptext(url, self.cookies)
            self.parse_html_page(resp_again, url, index)
        elif html_title == '输入验证码 | OpenLaw':
            pass
            # self.decide_cookies(url, "", index)
        else:
            self.parse_html_page(resp, url, index)

    def parse_html_page(self, resp, url, index):
        """计算经js混淆解密后的html返回的数据总量，翻页次数，循环调用decide_cookies"""
        resp_html = etree.HTML(resp.text)
        html_title = resp_html.xpath('/html/head/title/text()')[0]
        if html_title == "裁判文书高级检索 | OpenLaw":
            randomkey = re.findall(r'randomKey= "(.+)";', resp.text)[0]
            search_count = resp_html.xpath('//*[@id="search-btn-bar"]/p/b/text()')[0]
            print("当前为{}".format(index))
            if 0 < int(search_count) <= 20:
                self.save_to_mongo(resp_html, randomkey)
            elif 20 < int(search_count):
                self.save_to_mongo(resp_html, randomkey)
                pages = math.ceil(int(search_count)/20)
                if pages > 20:
                    pages = 20
                if index+1 <= pages:
                    time.sleep(3)
                    next_page_url = re.sub(r"page=\d*", "page="+str(index+1), url)
                    next_resp = self.parse_resptext(next_page_url, self.cookies)
                    self.decide_cookies(next_page_url, next_resp, index+1)
        else:
            self.decide_cookies(url, "", index)

    def save_to_mongo(self, resp_html, randomkey):
        """从html中提取数据保存"""
        article_list = resp_html.xpath('//*[@id="ht-kb"]//article')
        for article in article_list:
            encrypt_js_id = article.xpath('./h3/a/@onclick')
            encrypt_id = re.findall(r"visitPage\('(.+?)'", encrypt_js_id[0])[0]
            decryption_id = self.decrypt_id(encrypt_id, randomkey)
            title = article.xpath('./h3/a/text()')
            judge_date = article.xpath('./ul/li[@class="ht-kb-em-date"]/text()')
            court = article.xpath('./ul/li[@class="ht-kb-em-author"]/a/text()')
            ctype = article.xpath('./ul/li[@class="ht-kb-em-category"]/a/text()')
            number = article.xpath('./ul/li[@class="ht-kb-em-category"][last()]/text()')
            item = dict(
                Document_id=decryption_id,
                Case_name=title[0] if title else "",
                Judge_date=judge_date[0] if judge_date else "",
                Court_name=court[0] if court else "",
                Case_type=ctype[0] if ctype else "",
                Case_number=number[0] if number else "",
                Upload_date=datetime.date.today().strftime("%Y-%m-%d"),
                status=False
            )
            query = {"Document_id": item["Document_id"]}
            p = openlaw_list_model.find_one_by_query(query)
            if not p:
                openlaw_list_model.insert(item)
                print("{}保存成功".format(item["Document_id"]))
            else:
                print("{}已存在".format(item["Document_id"]))

    def parse_resptext(self, url, cookies):
        """封装requests进行复用"""
        for _ in range(5):
            try:
                resp = requests.get(url, cookies=cookies, headers=self.headers)
            except:
                time.sleep(5)
                continue
            else:
                if resp.status_code == 200:
                    return resp
                else:
                    time.sleep(5)
                    continue

    def get_mixencrypt_cookies(self, resp):
        """解密js的混淆加密，生成访问正常html的cookies，通过self.cookies的字典可变属性进行实时更新"""
        code = re.findall(r"\$\.\$\(\$\.\$\((.+)\)\(\)\)\(\)", resp.text)[0]
        mix_encrypt_js = execjs.compile(self.mix_encrypt)
        return_js_for_cookies = mix_encrypt_js.call("mixEncrypted", code)
        js_for_cookies = re.findall(r'return"(.+?)"$', return_js_for_cookies, re.S)[0]
        decode_js_content = self.handle_js_for_cookies(js_for_cookies)
        cookies_list = re.findall(r"document\.cookie='(.*?)'", decode_js_content, re.S)
        which_var = re.findall(r"\+_process\((\w+)\);", decode_js_content, re.S)[0]
        var_value = re.findall(r'var %s = "(.+?)";var' % which_var, resp.text.replace('\n', ''), re.S)[0]
        func_js_content = re.findall(r"(function _process\(s\).+;};)var", decode_js_content, re.S)[0]
        ctx = execjs.compile(func_js_content)
        join_cookies = ctx.call("_process", var_value)
        cookies_list[0] += var_value
        cookies_list[-1] += join_cookies
        self.cookies.update({cookie.split("=")[0]: cookie.split("=")[1] for cookie in cookies_list})

    @staticmethod
    def handle_js_for_cookies(js_for_cookies):
        """get_mixencrypt_cookies函数解密js后返回ascii码的js代码，进行转码"""
        js_content_list = js_for_cookies.split("\\")
        decode_js_content_list = []
        for js_content in js_content_list:
            ascii_number_search = re.search(r"(\d{2,3})", js_content)
            if ascii_number_search:
                ascii_number = ascii_number_search.group()
                if int(ascii_number) > 177:
                    ascii_number = ascii_number[0:2]
                decode_js_content = js_content.replace(ascii_number, chr(eval('0o'+str(int(ascii_number)))))
                decode_js_content_list.append(decode_js_content)
            else:
                decode_js_content_list.append(js_content)
        decode_js_content = "".join(decode_js_content_list).replace("@", "100")
        return decode_js_content

    def decrypt_id(self, encrypt_id, randomkey):
        """解密文书id，编译js并传参"""
        _processs_ctx = execjs.compile(self.data_process)
        decryption_id = _processs_ctx.call("decryptByDES", encrypt_id, randomkey)
        return decryption_id


"""
class OpenlawGetCourtSpider(OpenlawListSpider):

    name = "openlaw.cn.court_get"
    allowed_domain = ["openlaw.cn"]

    def __init__(self, *args, **kwargs):
        super(OpenlawGetCourtSpider, self).__init__(*args, **kwargs)
        self.start_url = "http://openlaw.cn/search/judgement/court"

    def start_requests(self):
        resp = self.parse_resptext(self.start_url, self.cookies)
        html = etree.HTML(resp.text)
        a_element_list = html.xpath('//*[@id="judgement-filters"]/div/div//a')
        for a_element in a_element_list:
            a_href = a_element.xpath('./@href')[]
            zone = re.findall(r"zone=(.*)", a_href)
            if not zone:
                court_id = re.findall(r"courtId=(.+)", a_href)[0]
                item = dict(
                    court_id=court_id
                )
            else:
                pass

    def save_to_db(self):
        pass
"""
