#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import hashlib
import re
from datetime import datetime

import scrapy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from ..items import JobBoleArticleItem, JobBoleArticle


class JobBolePostsSpider(scrapy.Spider):
    name = 'JobBolePostsSpider'
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def start_requests(self):
        mysql_host = self.crawler.settings.get("MYSQL_HOST")
        mysql_port = self.crawler.settings.get("MYSQL_PORT")
        mysql_user = self.crawler.settings.get("MYSQL_USER")
        mysql_password = self.crawler.settings.get("MYSQL_PASSWORD")
        mysql_db_name = self.crawler.settings.get("MYSQL_DB_NAME")
        engine = create_engine('mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(mysql_user, mysql_password,
                                                                              mysql_host, mysql_port,
                                                                              mysql_db_name),
                               pool_recycle=180, echo=False)
        session_maker = sessionmaker(bind=engine)
        self.db_session = session_maker()

        for url in self.start_urls:
            yield scrapy.Request(url)

    def parse(self, response):
        if self.db_session is None:
            self.logger.error("db_session is None")
            return None

        """
        1.获取文章列表也中具体文章url,并交给scrapy进行下载后并进行解析
        2.获取下一页的url并交给scrapy进行下载，下载完成后，交给parse
        :param response:
        :return:
        """
        if response is None:
            self.logger.warn("文章列表页响应为空，不做处理！")
        else:
            post_nodes = response.css('#archive .floated-thumb .post-thumb a')
            for post_node in post_nodes:
                post_url = post_node.css('::attr(href)').extract_first().strip()
                url_object_id = self.get_md5(post_url)
                count = 0
                try:
                    count = self.db_session.query(func.count()).filter(
                        JobBoleArticle.url_object_id == url_object_id).first()
                    if count:
                        count = count[0]
                except Exception as e:
                    self.logger.error("查询数据库异常，原因：{}".format(e))

                if count:
                    self.logger.info("数据库已有该数据url_object_id：%s" % url_object_id)
                    continue
                else:
                    image_url = post_node.css('img::attr(src)').extract_first().strip()
                    yield response.follow(url=post_url,
                                          meta={"front_image_url": image_url},
                                          callback=self.parse_detail)

            # 提取下一页并交给scrapy下载
            next_url = response.css('.next.page-numbers::attr(href)').extract_first()
            if next_url:
                self.logger.info("Next page：%s" % next_url)
                yield response.follow(next_url, self.parse)
            else:
                self.logger.info("None Next page!")
                self.db_session.close()

    def parse_detail(self, response):
        """
        获取文章的详细内容
        :param response:
        :return:
        """
        article_item = JobBoleArticleItem()
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图地址
        title = response.xpath('//*[@class="entry-header"]/h1/text()').extract_first()
        create_date = response.xpath('//div[@class="entry-meta"]/p/text()').extract_first().strip().split()[0]
        tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a[position()>1]/text()').extract()
        tag = [e for e in tag_list if not e.strip().endswith("评论")]
        praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract_first()
        if praise_nums:
            praise_nums = int(praise_nums)
        else:
            praise_nums = 0

        fav_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract_first()
        fav_nums = re.match(".*(\d+).*", str(fav_nums))
        if fav_nums:
            fav_nums = int(fav_nums.group(1))
        else:
            fav_nums = 0

        comment_nums = response.xpath('//a[@href="#article-comment"]/text()').extract_first()
        comment_nums = re.match(".*(\d+).*", str(comment_nums))
        if comment_nums:
            comment_nums = int(comment_nums.group(1))
        else:
            comment_nums = 0

        # content = response.xpath('//div[@class="entry"]').extract_first()
        content = "由于内容会导致日志过长，所以不获取内容！"

        article_item["title"] = title

        try:
            create_date = datetime.strptime(create_date, '%Y/%m/%d').date()
            create_date = datetime.combine(create_date, datetime.min.time())
        except Exception as e:
            create_date = datetime.today()

        article_item["url"] = response.url
        article_item["url_object_id"] = self.get_md5(response.url)  # 这里对地址进行了md5变成定长
        article_item["front_image_url"] = [front_image_url]
        article_item["create_date"] = create_date
        article_item["praise_nums"] = praise_nums
        article_item["fav_nums"] = fav_nums
        article_item["comment_nums"] = comment_nums
        article_item["tag"] = tag
        article_item['content'] = content

        yield article_item

    @staticmethod
    def get_md5(param):
        if isinstance(param, str):
            param = param.encode()
        m = hashlib.md5()
        m.update(param)
        return m.hexdigest()
