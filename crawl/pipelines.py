# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json

import pymongo
import pymysql
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi


class CustomTwistedMongoDBPipline(object):
    """
    MongoDb的异步存储，配合scrapy的异步性能
    """

    def open_spider(self, spider):
        """
        爬虫启动时执行
        """
        # mongo_key为settings中的DATABASES数据库配置键
        # mongo_coll为 ${db.collection}，以'.'连接
        # if not all([hasattr(spider, "mongo_key"), hasattr(spider, "mongo_coll")]):
        #     return
        # mongo_key = spider.mongo_key
        # mongo_config = spider.settings.get('DATABASES').get(mongo_key)
        # self.client = self._get_client(mongo_config)
        # spider.logger.info("连接mongodb成功")
        # mongo_coll = spider.mongo_coll
        # self.coll = self._get_coll(mongo_coll)
        if not hasattr(spider, "mongodb_model"):
            return
        db_instance = spider.mongodb_model()
        self.client = db_instance.client
        self.coll = db_instance.coll
        spider.logger.info("mongodb连接成功，使用collection名{}".format(self.coll.name))

    def close_spider(self, spider):
        """
        爬虫关闭时执行
        """
        if hasattr(self, "client"):
            self.client.close()
            spider.logger.info("mongodb连接关闭")

    @defer.inlineCallbacks
    def process_item(self, item, spider):
        if not hasattr(spider, "mongo_save"):
            func = self._update
        else:
            func = self._insert
        out = defer.Deferred()
        reactor.callInThread(func, item, out, spider)
        yield out
        defer.returnValue(item)

    def _insert(self, item, out, spider):
        """
        单条插入方法
        """
        self.coll.insert(dict(item))
        reactor.callFromThread(out.callback, item)

    def _update(self, item, out, spider):
        """
        单条更新方法，item中必须拥有一个uid字段
        """
        item = dict(item)
        assert item.get("uid")
        self.coll.update_one({"uid": item.get("uid")}, {"$set": item}, upsert=True)
        reactor.callFromThread(out.callback, item)

    def handle_error(self, failure, item, spider):
        spider.logger.error("存储mongodb出错，{}".format(failure))

    @staticmethod
    def _get_client(mongodb_config):
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

    def _get_coll(self, mongo_coll):
        db_name = mongo_coll.split(".")[0]
        coll_name = mongo_coll.split(".")[1]
        db = self.client[db_name]
        coll = db[coll_name]
        return coll


class CustomMysqlPipeline(object):
    """
    同步存储数据到mysql
    """
    def __init__(self):
        self.conn = pymysql.connect("host", "user", "pwd", "db", charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        """
        需要在item中定义sql语句方法，get_insert_sql
        :param item:
        :param spider:
        :return:
        """
        insert_sql, params = item.get_insert_sql()
        self.cursor.execute(insert_sql, params)
        self.conn.commit()


class CustomTwistedMysqlPipeline(object):
    """
    异步存储数据到Mysql
    """
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            db=settings["MYSQL_DBNAME"],
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        spider.logger.error("存储mysql出错，{}".format(failure))

    def do_insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


class CustomJsonWithEncodingPipeline(object):
    """
    """
    def __init__(self):
        self.file = codecs.open("aticle.json", "w", encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False)
        self.file.write(lines)
        return item

    def spider_close(self, spider):
        self.file.close()


class CustomJsonExporterPipeline(object):
    """
    调用scrapy提供的json export导出json文件
    """

    def __init__(self):
        self.file = open("aticleexporter.json", "wb")
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def clsoe_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class CustomImagesPipeline(ImagesPipeline):
    """
    重写ImagesPipeline方法，使保存的图片名称和路径自定义
    """
    def get_media_requests(self, item, info):
        for img_url in item["img_urls"]:
            yield scrapy.Request(img_url, meta={"item": item})

    def file_path(self, request, response=None, info=None):
        item = request.meta.get("item", "")
        img_title = item["img_name"]
        return 'full/%s.jpg' % img_title
