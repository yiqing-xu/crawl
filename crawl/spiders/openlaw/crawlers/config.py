#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : xuyiqing
# @Time    : 2019/8/15 9:20
# @File    : config.py
# @Software: PyCharm
import os
import json
import time
from urllib.parse import urlencode

import requests
import pandas as pd
from crawl.settings import STATICS_DIR

from utils.proxy import proxies
from .openlaw_login_encrypt import OpenlawLoginSpider
from ..models import OpenlawCourtIdModel

query_string_parameters = """
    showResults:
    keyword:
    causeId:
    caseNo:
    litigationType:
    docType:
    litigant:
    plaintiff:
    defendant:
    thirdParty:
    lawyerId:
    lawFirmId:
    legals:
    courtId:
    judgeId:
    clerk:
    judgeDateYear:
    judgeDateBegin:
    judgeDateEnd:
    procedureType:
    lawId:
    lawSearch:
    courtLevel:
    judgeResult:
    page:
"""

dates = pd.date_range(start="2019-07-01", end="2019-07-06", freq="5D")

with open(os.path.join(STATICS_DIR, "court.json"), "r", encoding="utf-8") as f:
    court_info = json.loads(f.read())


class OpenlawCourtIdSpider(OpenlawLoginSpider):
    """
    openlaw网站的案例文书检索条件\n
    1、裁判日期 --- 2019-01-01至2019-02-01\n
    2、地区 --- 省级地区检验，当在省级检索结果下再次点击地市级会取消地区检验条件\n
    3、法院 --- 法院id，通过"http://openlaw.cn/service/rest/opendata.Search/collection/courtSuggestion?"动态返回法院id
    """
    """综合采用<裁判日期> + <法院id>来实现案例文书的采集工作"""

    name = "openlaw.cn.court"
    allowed_domain = ["openlaw.cn"]

    def __init__(self, *args, **kwargs):
        super(OpenlawCourtIdSpider, self).__init__(*args, **kwargs)
        self.params_data = {params.strip(): "" for params in query_string_parameters.split(":") if params.strip()}
        self.date_list = [date.strftime("%Y-%m-%d") for date in dates]
        self.openlaw_courtid_model = OpenlawCourtIdModel()
        self.courtsug_url = "http://openlaw.cn/service/rest/opendata.Search/collection/courtSuggestion?"

    def start_requests(self):
        cookies = {"SESSION": "YzZiNDk4Y2YtNWVjNS00ZjhjLWJjNTQtNmMzNzYwYWVjMjBh"}
        court_name_list = [court["name"] for k, court in court_info.items()]
        print(len(court_name_list))
        for court_name in court_name_list[::-1]:
            query_string = {"keyword": "{}".format(court_name)}
            court_url = self.courtsug_url + urlencode(query_string)
            for _ in range(5):
                try:
                    time.sleep(2)
                    resp = requests.get(court_url, cookies=cookies, headers=self.headers)
                except Exception as e:
                    print(e)
                    time.sleep(5)
                    continue
                else:
                    if resp.status_code == 200:
                        if resp.text:
                            self.parse_resp(resp.text)
                        break
                    else:
                        time.sleep(5)
                        continue

    def parse_resp(self, text):
        resp_text = json.loads(text)
        for suggest_court in resp_text:
            item = suggest_court
            item["court_id"] = suggest_court.pop("id")
            query = {"court_id": item["court_id"]}
            p = self.openlaw_courtid_model.find_one_by_query(query)
            if not p:
                self.openlaw_courtid_model.insert(item)
