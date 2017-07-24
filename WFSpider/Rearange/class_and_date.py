# coding: utf-8

import pymongo
import re
import time
import math
from pprint import pprint

cli = pymongo.MongoClient('localhost', 27017)
db = cli.WanFang


def to_timestamp(base):
    time_list = list(re.match('(\d+)[^\d]+(\d+)[^\d]+(\d+)[^\d]+', base).groups()) + [0 for i in range(6)]
    time_list = map(int, time_list)
    return time.mktime(time_list)


n = 0

while 1:
    item = db.Article.find_one({'_class': {"$exists": False}})
    if not item:
        print "Done"
        break
    try:
        class_info = db.Journal.find_one({'url': item['journal_url']})
        info_to_update = {}
        info_to_update['_class'] = class_info['_class']
        info_to_update['sub_class'] = class_info['sub_class']
        info_to_update['ol_publish_timestamp'] = to_timestamp(item['ol_publish_time'][0])
        item = db.Article.find_one_and_update({'_id': item['_id']},
                                              {'$set': info_to_update})
    except Exception, e:
        pprint(item)
        print e.__class__.__name__, e
    n += 1
    if math.fmod(n, 10000) == 0:
        pprint(n)
