# coding: utf-8

from db import mongo_cli
from bson.objectid import ObjectId


def search(range_limit, words):
    words = words.split()
    concerned = {'title': ['title',
                           'title_global'],
                 'author': ['author',
                            'author_global'],
                 'abstract': ['abstract'],
                 'ol_publish_time': ['ol_publish_time'],
                 'fulltext': ['title',
                              'title_global',
                              'author',
                              'author_global',
                              'abstract',
                              'ol_publish_time',
                              'journal_name',
                              'journal_url',
                              'abstract',
                              'company']}[range_limit]
    exp = exp_gen(concerned, words)
    return mongo_cli.article.find(exp), \
           mongo_cli.article.find(exp).count()


def exp_gen(concerned, words):
    return {"$or":
        [
            {"$and":
                [
                    {key: {"$regex": word}}
                    for word in words
                ]
            }
            for key in concerned
        ]
    }


def _remove_duplicate(target):
    tmp = []
    for item in target:
        if item not in tmp:
            yield item
            tmp.append(item)


def get_by_id(object_id_str):
    return mongo_cli.article.find_one({'_id': ObjectId(object_id_str)})


def get_all_main_class():
    res = mongo_cli.mainindex.find({})
    return ((item['class_name'][0].strip(), item['_id'])
            for item in res)


def gen_time_query(_from, _to):
    res = {}
    if _from:
        res.update({"$gte": _from, })
    if _to:
        res.update({"$lte": _to})
    return res


def get_popular_keywords(target,
                         _from=None,
                         _to=None,
                         class_id=None):
    target = ["keywords", "author"][target]
    query_filter = {target: {"$exists": True}}

    if _from or _to:
        query_filter.update({"ol_publish_timestamp": gen_time_query(_from, _to)})
    if class_id:
        query_filter.update({"_class._id": ObjectId(class_id)})
    keywords_dct = {}

    for item in mongo_cli.article.find(query_filter):
        for keyword in item[target]:
            if keywords_dct.get(keyword):
                keywords_dct[keyword] += 1
            else:
                keywords_dct[keyword] = 1
    return top100(keywords_dct)  # name, mount


def top100(dct):
    return sorted(dct.items(),
                  key=lambda x: x[1],
                  reverse=True)[:100]
