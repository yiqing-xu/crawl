# -*- coding: utf-8 -*-
# @Time    : 2020/3/10 11:52
# @Author  : xuyiqing
# @File    : mongodblib.py
import pymongo

from crawl.settings import DATABASES


class MongoDb(object):
    mongo_key = ""
    mongo_coll = ""

    def __init__(self):
        self.client = self.get_client()
        self.coll = self.get_coll()
        if 'uid_1' not in self.coll.index_information():
            self.coll.create_index([('uid', 1)])

    def get_client(self):
        mongodb_config = DATABASES.get(self.mongo_key)
        host = mongodb_config["host"]
        port = mongodb_config["port"]
        if mongodb_config.get("replicaset"):
            client = pymongo.MongoClient("{host}:{port}".format(
                host=host,
                port=port,
            ), replicaset="gtSet", connect=False)
        else:
            if mongodb_config.get("user"):
                import urllib.parse as urlparse
                db = mongodb_config["db"]
                host = "%s:%s/%s" % (host, str(port), db)
                uri = "mongodb://%s:%s@%s" % (
                    urlparse.quote_plus(mongodb_config["user"]),
                    urlparse.quote_plus(mongodb_config["password"]), host)
                client = pymongo.MongoClient(uri, connect=False)
            else:
                client = pymongo.MongoClient(host, port, connect=False)
        return client

    def get_coll(self):
        db_name = self.mongo_coll.split(".")[0]
        coll_name = self.mongo_coll.split(".")[1]
        db = self.client[db_name]
        coll = db[coll_name]
        return coll

    def yield_documents(self, size=1000, query=None, _source=None, sort=None):
        global _id
        _id = None
        if query is None:
            filter = {}
        else:
            filter = query

        kwargs = {}
        kwargs["sort"] = [("_id", pymongo.ASCENDING)]
        if sort:
            kwargs["sort"].extend(sort)
        if _source:
            kwargs["projection"] = _source

        while True:
            documents = []
            if _id:
                filter.update({"_id": {"$gt": _id}})

            cr = self.coll.find(filter, **kwargs).limit(size)
            for document in cr:
                documents.append(document)
            if documents:
                _id = documents[-1]["_id"]
                yield documents
            else:
                break
