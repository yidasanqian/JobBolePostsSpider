#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from scrapy import cmdline

if __name__ == '__main__':
    cmd = "scrapy crawl JobBolePostsSpider".split()
    cmdline.execute(cmd)
