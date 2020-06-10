#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : xuyiqing
# @Time    : 2019/8/14 15:52
# @File    : openlaw_login_encrypt.py
# @Software: PyCharm
import os
import base64
from copy import deepcopy

import requests
import execjs
from lxml.html import etree
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from fake_useragent import UserAgent
from scrapy import Spider
from crawl.settings import BASE_DIR

from utils.proxy import proxies


os.environ["EXECJS_RUNTIME"] = "Node"
data_path = os.path.join(BASE_DIR, "crawl/spiders/openlaw/static")


class OpenlawJsEncryptRead(Spider):

    def __init__(self, *args, **kwargs):
        super(OpenlawJsEncryptRead, self).__init__(*args, **kwargs)
        with open(os.path.join(data_path, "encrypt.js.jsp"), "r", encoding="utf-8") as r:
            self.encrypt_js_jsp = r.read()
        with open(os.path.join(data_path, "jsencrypt.min.js"), "r", encoding="utf-8") as r:
            self.jsencrypt_min_js = r.read()
        with open(os.path.join(data_path, "aes.js"), "r", encoding="utf-8") as r:
            self.aes_js = r.read()
        with open(os.path.join(data_path, "pbkdf2.js"), "r", encoding="utf-8") as r:
            self.pbkdf2 = r.read()
        with open(os.path.join(data_path, "mix_encrypt.js"), "r", encoding="utf-8") as r:
            self.mix_encrypt = r.read()
        with open(os.path.join(data_path, "list-data-process.js"), "r", encoding="utf-8") as r:
            self.data_process = r.read()


class OpenlawLoginSpider(OpenlawJsEncryptRead):

    def __init__(self, *args, **kwargs):
        super(OpenlawLoginSpider, self).__init__(*args, **kwargs)
        self.start_url = "http://openlaw.cn/login.jsp"
        self.login_url = "http://openlaw.cn/login"
        self.headers = {
            "User-Agent": UserAgent().chrome,
            "Host": "openlaw.cn"
        }
        self.password = ""
        self.login_data = {
            "username": "",
            "_spring_security_remember_me": "true"
        }

    def start_login(self):
        # openlaw的cookies绑定ip
        resp = requests.get(self.start_url, headers=deepcopy(self.headers))
        if resp.status_code == 200:
            return resp

    def login_parse(self):
        resp = self.start_login()
        if resp.status_code == 200:
            cookies_jsp = requests.utils.dict_from_cookiejar(resp.cookies)
            resp_html = etree.HTML(resp.text)
            csrf = resp_html.xpath('//*[@id="login-form"]/input/@value')[0]
            self.login_data.update({"_csrf": csrf})
            js_content = execjs.compile(self.encrypt_js_jsp + self.aes_js + self.pbkdf2)
            encrypt_pwd_param = js_content.call("keyEncrypt", self.password)
            encrypt_pwd_value = self.encrypt_pwd(encrypt_pwd_param)
            self.login_data.update({"password": encrypt_pwd_value})
            return cookies_jsp

    def login(self):
        cookies_jsp = self.login_parse()
        resp = requests.post(
            self.login_url,
            data=self.login_data,
            cookies=cookies_jsp,
            headers=deepcopy(self.headers),
        )
        cookie = resp.request.headers.get("Cookie")
        if cookie:
            cookie_k_v = cookie.split("=")
            cookies = {cookie_k_v[0]: cookie_k_v[1]}
            return cookies

    @staticmethod
    def encrypt_pwd(encrypt_pwd_param):
        publicKey = '-----BEGIN PUBLIC KEY-----\n\
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0zI8aibR9ZN57QObFxvI\n\
        wiRTmELItVVBLMrLd71ZqakR6oWUKkcAGgmxad2TCy3UeRe4A0Dduw97oXlbl5rK\n\
        RGISzpLO8iMSYtsim5aXZX9SB5x3S9ees4CZ6MYD/4XQOTrU0r1TMT6wXlhVvwNb\n\
        fMNYHm3vkY0rhfxBCVPFJoHjAGDFWNCAhf4KfalfvWsGL32p8N/exG2S4yXVHuV6\n\
        cHDyFJAItKVmyuTmB62pnPs5KvNv6oPmtmhMxxsvBOyh7uLwB5TonxtZpWZ3A1wf\n\
        43ByuU7F3qGnFqL0GeG/JuK+ZR40LARyevHy9OZ5pMa0Nwqb8PwfK810Bc8PxD8N\n\
        EwIDAQAB\n\
        -----END PUBLIC KEY-----\n\
        '
        rsakey = RSA.importKey(publicKey)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
        cipher_text = base64.b64encode(cipher.encrypt(encrypt_pwd_param[0].encode(encoding="utf-8")))  # 对密码字符串加密
        value = cipher_text.decode('utf8')  # 将加密获取到的bytes类型密文解码成str类型
        return value + ":::" + encrypt_pwd_param[1]
