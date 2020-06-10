#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : xuyiqing
# @Time    : 2019/8/12 11:14
# @File    : models.py
# @Software: PyCharm
from microserver.db.mongodb import MongoDB


class OpenlawCourtIdModel(MongoDB):

    _name = "openlaw.court_id"
    _alias_name = "mongodb"

    PRIMARY_KEY = None


class OpenlawListModel(MongoDB):

    _name = "openlaw.list"
    _alias_name = "mongodb"

    PRIMARY_KEY = None


class OpenlawCourtGetModel(MongoDB):

    _name = "openlaw.court_get"
    _alias_name = "mongodb"

    PRIMARY_KEY = None


class OpenlawDetailModel(MongoDB):

    _name = "openlaw.detail"
    _alias_name = "mongodb"

    PRIMARY_KEY = None
