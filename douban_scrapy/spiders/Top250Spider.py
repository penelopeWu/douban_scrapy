from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.spiders import Rule, CrawlSpider

from douban_scrapy.items import DoubanScrapyItem


class Top250Spider(CrawlSpider):  # 多页爬取继承CrawlSpider
    name = "top250spider"

    download_delay = 1

    allowed_domains = []

    start_urls = [
        'https://movie.douban.com/top250?start=0&filter='
    ]

    # 多页爬取规则
    rules = (
        Rule(LinkExtractor(allow=(r'\?start=\d+&filter=')), callback='parse_item',
             # Rule(LinkExtractor(allow=(r'http://movie\.douban\.com/top250\?start=\d+&filter=')), callback='parse_item',
             follow=True),
    )

    # 多页爬取
    def parse_item(self, response):
        print("========= parse_item ========")
        selector = Selector(response)
        item = DoubanScrapyItem()

        movies = selector.xpath('//div[@class="info"]')
        for movie in movies:

            movie_name = movie.xpath('div[@class="hd"]/a/span/text()').extract()
            full_name = ''
            for name in movie_name:
                full_name += name
            movie_url = movie.xpath('div[@class="hd"]/a/@href').extract_first   ()
            star = movie.xpath('div[@class="bd"]/div[@class="star"]/span[@class="rating_num"]/text()').extract_first()
            quote = movie.xpath('div[@class="bd"]/p/span[@class="inq"]/text()').extract_first()
            if quote:
                quote = quote[0]
            else:
                quote = ''
            item['movie_name'] = full_name
            item['movie_url'] = movie_url
            item['star'] = star
            item['quote'] = quote
            yield item


        #这种方式不好，因为有些记录没有playable,导致最终的数据少了
        # for name, url, pl, st, qu in zip(movie_name, movie_url, playable, star, quote):
        #     item['movie_name'] = name
        #     item['movie_url'] = url
        #     item['playable'] = pl
        #     item['star'] = st
        #     item['quote'] = qu
        #     yield item



    # 单页爬取
    # def parse(self, response):
    #     selector = Selector(response)
    #     item = DoubanScrapyItem()
    #
    #     movie_name = selector.xpath('//span[@class="title"][1]/text()').extract()
    #     movie_url = selector.xpath('//div[@class="hd"]/a/@href').extract()
    #     playable = selector.xpath('//span[@class="playable"]/text()').extract()
    #     star = selector.xpath('//span[@class="rating_num"]/text()').extract()
    #     quote = selector.xpath('//span[@class="inq"]/text()').extract()
    #
    #     for name,url,pl,st,qu in zip(movie_name,movie_url,playable,star,quote):
    #         item['movie_name'] = name
    #         item['movie_url'] = url
    #         item['playable'] = pl
    #         item['star'] = st
    #         item['quote'] = qu
    #         yield item
