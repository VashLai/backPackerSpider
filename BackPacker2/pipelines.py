# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from .settings import *


class Backpacker2Pipeline(object):
    count = 0

    def process_item(self, item, spider):
        self.count += 1

        print('寫入次數：', self.count)
        # print('first_link:', item['first_link'])
        # print('sec_link:', item['sec_link'])
        # print('total_page:', item['total_page'])
        # print('url:', item['url'])
        print('大分類標題：', item['name'])
        print('文章分類：', item['category'])
        print('文章標題：', item['title'])
        print('文章號碼：', item['articleNum'])
        print('文章連結：', item['link'])
        print('文章回覆數：', str(item['reports']))
        # print('內文：', item['message'])
        print('*' * 50)
        return item


class Backpacker2MysqlPipeline(object):
    count = 0

    def open_spider(self, spider):
        self.db = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PWD,
            database=MYSQL_DB,
            charset=MYSQL_CHARSET
        )
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        ins = 'insert into backpacker(name, category, title, articlenum, url, reports) values(%s, %s, %s, %s, %s, %s)'
        L = [
            item['name'],
            item['category'],
            item['title'],
            item['articleNum'],
            item['link'],
            item['reports'],
        ]
        self.cursor.execute(ins, L)
        self.db.commit()
        self.count += 1
        print('寫入次數：', self.count, '新增：', item)
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.db.close()
