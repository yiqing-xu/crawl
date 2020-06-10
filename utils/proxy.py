# -*- coding: utf-8 -*-
# @Time    : 2020/2/25 16:57
# @Author  : xuyiqing
# @File    : proxy.py
import base64

proxyServer = "http://http-dyn.abuyun.com:9020"

proxyUser = ""
proxyPass = ""
# for Python2
# proxyAuth = "Basic " + base64.b64encode(proxyUser + ":" + proxyPass)

# for Python3
proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")


proxyHost = "http-pro.abuyun.com"
proxyPort = "9010"

proxyUser = ""
proxyPass = ""

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host": proxyHost,
    "port": proxyPort,
    "user": proxyUser,
    "pass": proxyPass,
}
proxies = {
    "http": proxyMeta,
    "https": proxyMeta,
}
