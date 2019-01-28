# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    movie_name = scrapy.Field()
    movie_url = scrapy.Field()
    star = scrapy.Field()
    quote = scrapy.Field()
    pass
