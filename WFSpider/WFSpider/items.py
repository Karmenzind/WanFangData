# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import (Item, Field)

class ArticleItem(Item):
    """
    文章页面
    """
    _id = Field()
    title = Field()
    title_global = Field() # 其他语言
    abstract = Field()

    author = Field() # 中、英、搜索链接
    author_global = Field()
    company = Field()  # 单位

    journal_name = Field()
    journal_url = Field()
    publish_issue = Field()
    ol_publish_time = Field()

    keywords = Field()

    from_url = Field()
    dl_url = Field()

class JournalItem(Item):
    """
    期刊页面
    """
    _id = Field()
    _class = Field()
    sub_class = Field()
    name = Field()
    url = Field()
    rss = Field()


"""
# For index 👇
"""

class SubjectItem(Item):
    """
    类&二级类
    """
    _id = Field()
    class_name = Field()
    class_url = Field()
    sub_class = Field()

"""
# For filtering
"""

class PublishTimeItem(Item):
    p_time = Field()
    from_url = Field()