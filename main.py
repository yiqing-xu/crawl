# -*- coding: utf-8 -*-
# @Time    : 2020/2/25 16:00
# @Author  : xuyiqing
# @File    : main.py
from scrapy.cmdline import execute
import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "list"])
execute(["scrapy", "crawl", ""])
