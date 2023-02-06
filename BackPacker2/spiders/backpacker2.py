# -*- coding: utf-8 -*-
import scrapy
from ..items import Backpacker2Item
from ..settings import *
import re
import pymysql
from datetime import datetime


class Backpacker2Spider(scrapy.Spider):
    begin = datetime.now()
    name = 'backpacker2'
    allowed_domains = ['www.backpackers.com.tw']
    # allowed_domains = ['www.backpackers.com.tw']
    start_urls = ['https://www.backpackers.com.tw/forum/forumdisplay.php?f=4/']
    count = 0

    # 功能函數
    def db_close(self, db, cursor):
        cursor.close()
        db.close()

    # 解析一級頁面函數
    def parse(self, response):
        first_list = response.xpath('//tr[position()>2][position()<10]/td/div/div[3]/div[1]/a')
        for first in first_list:
            item = Backpacker2Item()
            first_link = "https://" + self.allowed_domains[0] + "/forum/" + first.xpath('./@href').get()
            item['name'] = first.xpath('./strong/text()').get()
            yield scrapy.Request(
                url=first_link,
                # meta是在不同解析函數之間傳遞參數用的
                meta={'item': item, 'first_link': first_link},
                callback=self.parse_two_page,
                dont_filter=True
            )

    # 解析二級頁面函數：頁碼
    def parse_two_page(self, response):
        # 先從一級解析函數接收item
        item = response.meta['item']
        first_link = response.meta['first_link']
        total_page = response.xpath('//*[@class="vbmenu_control"]/text()').get()
        total_page = int(re.findall('-?[0-9]+', total_page)[1])
        yield scrapy.Request(
            url=first_link,
            meta={'item': item, 'first_link': first_link, 'total_page': total_page},
            callback=self.parse_three_page,
            dont_filter=True
        )

    # 解析三級頁面函數：
    def parse_three_page(self, response):
        # 先從二級解析函數接收item
        item = response.meta['item']
        first_link = response.meta['first_link']
        total_page = response.meta['total_page']
        for page in range(1, total_page + 1):  # 測試時先把total_page + 1 改成3或2
            # for page in range(1, 3):  # 測試時先把total_page + 1 改成3或2
            url = first_link + '&page={}'.format(page)
            yield scrapy.Request(
                url=url,
                meta={'item': item},
                callback=self.parse_four_page,
                dont_filter=True
            )

    def parse_four_page(self, response):
        # 先從三級解析函數接收item
        print("正在爬取:", response.url)
        item = response.meta['item']
        sql1 = 'select articlenum from backpacker where articlenum={}'
        sql2 = 'select reports from backpacker where reports="{}" and articlenum={}'
        sql3 = 'update backpacker set reports="{}" where articlenum={}'

        li_list = response.xpath('//ul[contains(@id,"threadbits_forum_")]/li[contains(@class,"threadbit alt1")]')
        for li in li_list:
            db = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PWD, database=MYSQL_DB,
                                 charset=MYSQL_CHARSET)
            cursor = db.cursor()
            self.count += 1
            check_article = li.xpath('./@data-realthreadid').get()
            reports = li.xpath('./div[4]/span/text()').get()
            # res1 = cursor.execute(sql1.format(check_article)).fetchone()
            # res1 = cursor.execute(sql1.format(check_article)).fetchall()
            try:
                cursor1 = db.cursor()
                res1 = cursor1.execute(sql1.format(check_article))
                cursor1.close()
            except:
                print('res1失敗', res1)
            # check_url，若check_url不存在則提取資料後yield item，若存在則再檢查繼續檢查
            if res1 == 1:
                print("{}、檢查網頁中 {} 已存在於資料庫".format(self.count, check_article))
                print("{}、檢查網頁中 {} 中的reports是否與資料庫相同...".format(self.count, check_article))
                try:
                    cursor2 = db.cursor()
                    # res2_info = cursor2.mogrify(sql2.format(reports, check_article))
                    # print(res2_info)
                    res2 = cursor2.execute(sql2.format(reports, check_article))
                    cursor2.close()
                except Exception as e:
                    print("res2失敗", e)
                # res2 = cursor.fetchone()
                # reports，若resports與資料庫相同則不理會，若不相同則更新reports
                if res2 == 0:
                    print("{}、檢查 {} 中的reports:{} 與資料庫不相同，需更新".format(self.count, check_article, reports))
                    cursor.execute(sql3.format(reports, check_article))
                    print("{}、更新：{}".format(self.count, sql3.format(reports, check_article)))
                    print("*" * 20)
                    db.commit()
                    self.db_close(db, cursor)
                else:
                    print("{}、檢查網頁中reports：{}與資料庫相同，無需更新".format(self.count, reports))
                    print("*" * 20)
                    self.db_close(db, cursor)
            else:
                try:
                    item['articleNum'] = check_article
                except:
                    item['articleNum'] = ''
                try:
                    category = li.xpath('./div[@class="threadbit-body"]/span/text()').get()
                    item['category'] = re.findall('\w+', category)[0]
                except:
                    item['category'] = ''
                try:
                    item['title'] = li.xpath('./div[2]/a/text()').get()
                except:
                    item['title'] = '空'
                try:
                    item['link'] = 'https://www.backpackers.com.tw/forum/' + li.xpath('./div[2]/a/@href').get()
                except:
                    item['link'] = '空'
                try:
                    item['reports'] = reports
                except:
                    item['reports'] = 0
                self.db_close(db, cursor)
                yield item
