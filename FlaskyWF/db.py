# coding: utf-8
import pymongo


class MongoCli(object):
    def __init__(self):
        cli = pymongo.MongoClient(host="localhost",
                                  port=27017)
        db = cli['WanFang']
        self.article = db['Article']
        self.journal = db["Journal"]
        self.mainindex = db["MainIndex"]
        self.others = db["Others"]


mongo_cli = MongoCli()
