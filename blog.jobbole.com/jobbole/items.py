# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base


class JobBoleArticleItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    create_date = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()  # 文章下图片的url地址
    front_image_path = scrapy.Field()  # 图片的存放路径
    praise_nums = scrapy.Field()  # 点赞
    fav_nums = scrapy.Field()  # 收藏
    comment_nums = scrapy.Field()  # 评论
    tag = scrapy.Field()
    content = scrapy.Field()


# 创建对象的基类:
Base = declarative_base()


class JobBoleArticle(Base):
    __tablename__ = 'bole_posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(45))
    create_date = Column(DateTime)
    url = Column(String(160))
    url_object_id = Column(String(45), unique=True)
    front_image_url = Column(String(160))
    front_image_path = Column(String(160))
    praise_nums = Column(Integer)  # 点赞
    fav_nums = Column(Integer)  # 收藏
    comment_nums = Column(Integer)  # 评论
    tag = Column(String(160))
    content = Column(Text)

    def __init__(self, title, create_date, url, url_object_id, front_image_url, front_image_path, praise_nums, fav_nums,
                 comment_nums, tag, content):
        self.title = title
        self.create_date = create_date
        self.url = url
        self.url_object_id = url_object_id
        self.front_image_url = front_image_url
        self.front_image_path = front_image_path
        self.praise_nums = praise_nums
        self.fav_nums = fav_nums
        self.comment_nums = comment_nums
        self.tag = tag
        self.content = content
