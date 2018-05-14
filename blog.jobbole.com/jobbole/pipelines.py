# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .items import JobBoleArticle


class JobBolePostsMysqlPipeline(object):
    def __init__(self, mysql_host, mysql_port, mysql_user, mysql_password, mysql_db_name):
        # 初始化数据库连接:
        engine = create_engine('mysql+mysqlconnector://{}:{}@{}:{}/{}?charset=utf8'.format(mysql_user, mysql_password,
                                                                                           mysql_host, mysql_port,
                                                                                           mysql_db_name))
        # 创建session_maker类型:
        session_maker = sessionmaker(bind=engine)
        self.db_session = session_maker()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_host=crawler.settings.get("MYSQL_HOST"),
            mysql_port=crawler.settings.get("MYSQL_PORT"),
            mysql_user=crawler.settings.get("MYSQL_USER"),
            mysql_password=crawler.settings.get("MYSQL_PASSWORD"),
            mysql_db_name=crawler.settings.get("MYSQL_DB_NAME"),
        )

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self.db_session.close()

    def process_item(self, item, spider):
        """不下载图片，所以路径设为空"""
        front_image_path = ""

        title = item['title']
        create_date = item['create_date']
        url = item['url']
        url_object_id = item['url_object_id']
        front_image_url = ','.join(item['front_image_url'])
        praise_nums = item['praise_nums']
        fav_nums = item['fav_nums']
        comment_nums = item['comment_nums']
        tag = ','.join(item['tag'])
        content = item['content']

        jobbole_article = JobBoleArticle(title, create_date, url, url_object_id, front_image_url, front_image_path,
                                         praise_nums, fav_nums, comment_nums, tag, content)
        self.db_session.add(jobbole_article)
        try:
            # 提交即保存到数据库:
            self.db_session.commit()
        except Exception as e:
            spider.logger.error("插入数据库异常url_object_id:{}，原因：{}".format(url_object_id, e))
            self.db_session.rollback()
        return item


class JobBolePostsPipeline(object):
    collection_name = 'bole_posts'

    def __init__(self, mongo_host, mongo_port, mongo_db):
        self.client = pymongo.MongoClient(mongo_host, mongo_port)
        self.db = self.client[mongo_db]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_host=crawler.settings.get("MONGO_HOST"),
            mongo_port=crawler.settings.get("MONGO_PORT"),
            mongo_db=crawler.settings.get("MONGO_DB"),
        )

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self.client.close()

    # def process_item(self, item, spider):
    #     if item['front_image_path']:
    #         self.db[self.collection_name].insert_one(item)
    #         return item
    #     else:
    #         raise DropItem("Missing front_image_path field value")
    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(item)


class ArticleImagePipeline(ImagesPipeline):
    """
    对图片的处理
    """

    def item_completed(self, results, item, info):
        for ok, value in results:
            if ok:
                image_file_path = value["path"]
                item['front_image_path'] = image_file_path
            else:
                item['front_image_path'] = ""
        return item


class JobBolePostsDuplicatesPipeline(object):
    """
    一个用于去重的过滤器，丢弃那些已经被处理过的item,假设item有一个唯一的id，但是我们spider返回的多个item中包含了相同的id,
    去重方法如下：这里初始化了一个集合，每次判断id是否在集合中已经存在，从而做到去重的功能
    """

    def __init__(self):
        self.url_object_ids = set()

    def process_item(self, item, spider):
        url_object_id = item['url_object_id']

        if item['url_object_id'] in self.url_object_ids:
            raise DropItem("Duplicate url_object_id of item found: %s" % url_object_id)
        else:
            self.url_object_ids.add(url_object_id)
            return item
