# -*- coding: utf-8 -*-
# @Time    : 2020/4/22 9:39
# @Author  : xuyiqing
# @File    : models.py


from utils.mongodblib import MongoDb


class NpcModel(MongoDb):

    mongo_key = 'mongodb'
    mongo_coll = 'domain.npc_paraphrase'


class FixedNpcModel(MongoDb):

    mongo_key = 'mongodb'
    mongo_coll = 'domain.fixed_npc_paraphrase_1'


class QAModel(MongoDb):

    mongo_key = 'mongodb'
    mongo_coll = 'domain.qas'
