# -*- coding: utf-8 -*-
# @Time    : 2020/3/10 14:04
# @Author  : xuyiqing
# @File    : src_setup.py
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("BASE_DIR", BASE_DIR)
