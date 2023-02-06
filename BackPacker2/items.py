# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Backpacker2Item(scrapy.Item):

    # 1、一級頁面 - 第一批連結(first_link)、大分類標題(name)
    # first_link = scrapy.Field()
    name = scrapy.Field()

    # 2、二級頁面 - 第一批連結的總頁數
    # total_page = scrapy.Field()

    # 3、三級頁面為提取每一頁面的連結交由調度器後轉給第四級頁面
    #   - 文章分類(category)、文章編號(articleNum)、文章標題(title)、文章連結(link)、文章回覆數(reports)
    category = scrapy.Field()
    articleNum = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    reports = scrapy.Field()

    # 4、內文
    # message = scrapy.Field()
