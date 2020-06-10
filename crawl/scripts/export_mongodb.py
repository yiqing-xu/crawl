# -*- coding: utf-8 -*-
# @Time    : 2020/3/10 11:50
# @Author  : xuyiqing
# @File    : export_mongodb.py
import os
import time
import json
import datetime

import pandas as pd

import src_setup
from utils.mongodblib import MongoDb
from crawl.settings import DATA_DIR
from crawl.spiders.faxin.models import FaxinOutlineModel
from crawl.spiders.common.models import QAModel


class ExportFromMongo2Xlsx(QAModel):

    def __init__(self):
        super(ExportFromMongo2Xlsx, self).__init__()
        self.data_name = "{}_{}".format(self.mongo_coll, datetime.date.today())
        self.data_dir = os.path.join(DATA_DIR, "{}".format(self.data_name))
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.fields = ['question', "question_desc", "answer"]

    def export(self):
        start_time = time.time()
        documents = self.coll.find({}, {'question': 1, 'question_desc': 1, 'answer': 1})
        df = pd.DataFrame(documents)
        df.to_excel(os.path.join(self.data_dir, "{}.xlsx".format(self.data_name)), index=False, columns=self.fields)
        print("转excel耗时{}".format(time.time() - start_time))


class ExportTree2Json(FaxinOutlineModel):

    def __init__(self):
        super(ExportTree2Json, self).__init__()

    def export(self):
        data = []
        query = {"parent_dh": None}
        nodes = self.coll.find(query)
        self.get_children(nodes, data)
        with open(os.path.join(DATA_DIR, "faxin_outline.json"), "w", encoding="utf-8") as w:
            json.dump(data, w, ensure_ascii=False)

    def get_children(self, nodes, data):
        for node in nodes:
            item = dict()
            item["title"] = node["title"].strip()
            item["code"] = node["title_code"].strip()
            item["children"] = []
            data.append(item)

            sub_nodes = self.coll.find({"parent_dh": node["dh"]})
            if sub_nodes:
                print("查询到children，长度{}".format(sub_nodes.count()))
                self.get_children(sub_nodes, item["children"])


class ExportTree2Json2(FaxinOutlineModel):

    def __init__(self):
        super(ExportTree2Json2, self).__init__()
        self.documents = list(self.coll.find({}))

    def export(self):
        print(len(self.documents))
        import time
        time.sleep(5)
        data = []
        query = {"parent_dh": None}
        nodes = self.coll.find(query)
        # nodes = list(self.coll.find(query))
        # processes = len(nodes)
        # from multiprocessing import Pool
        # pool = Pool(processes=processes)
        # for i in range(processes):
        #     pool.apply_async(self.get_children, ([nodes[i]], data))
        # pool.close()
        # pool.join()
        # self.get_children(nodes, data)
        documents = [{"title": document["title"], "code": document["title_code"]} for document in self.documents]
        with open(os.path.join(DATA_DIR, "faxin_outline2.json"), "w", encoding="utf-8") as w:
            json.dump(documents, w, ensure_ascii=False)

    def get_children(self, nodes, data):
        for node in nodes:
            item = dict()
            item["title"] = node["title"].strip()
            item["code"] = node["title_code"].strip()
            item["children"] = []
            data.append(item)

            # sub_nodes = self.coll.find({"parent_dh": node["dh"]})
            # sub_nodes = []
            # for document in self.documents:
            #     if document["parent_dh"] == node["dh"]:
            #         sub_nodes.append(document)
            sub_nodes = [document for document in self.documents if document["parent_dh"] == node["dh"]]
            if sub_nodes:
                print("查询到children，长度{}".format(len(sub_nodes)))
                self.get_children(sub_nodes, item["children"])


def strip_faxin_outline():
    from pymongo import UpdateOne
    model = FaxinOutlineModel()
    documents = list(model.coll.find({}))
    requests = []
    for document in documents:
        request = UpdateOne({"_id": document["_id"]}, {"$set": {"title": document["title"].strip()}})
        requests.append(request)
    model.coll.bulk_write(requests)


if __name__ == '__main__':
    # db = ExportTree2Json2()
    # db.export()
    ExportFromMongo2Xlsx().export()
