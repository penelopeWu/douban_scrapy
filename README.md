## 环境
python                    3.6.8 
```
~ » scrapy version                                     penelope@wjj-PC
Scrapy 1.5.0
```

>！[上一篇文章中](http://mp.weixin.qq.com/s?__biz=MzU1OTI5OTcxNA==&mid=100000447&idx=1&sn=194e4eb27b6d90e9c1e2d55b422449cd&chksm=7c182f524b6fa6447b68a1bca8ea3c7e89bd47495a81242da77a6ffb3d606e17f42090e52bb7#rd)，我们使用scrapy创建了一个爬虫项目爬取了豆瓣电影榜单前十的数据。这只是小试牛刀，scrapy能做的可不止这些。今天我们来探索scrapy更厉害的功能。


首先，我们对没接触过爬虫的朋友做个知识普及：
典型的爬虫，会向2个方向移动：横向和纵向
前者我们称为水平爬取，因为这种情况下是在同一层级爬取页面（比如分页的数据，从第一页到第二页...)；

后者我们称为垂直爬取，因为该方式是从一个更高的层级到一个低层级的爬取。

我们今天要实现的是水平爬取豆瓣电影 Top 250

#分析网页
我们打开豆瓣电影 top 250的页面 https://movie.douban.com/top250
![](http://plqfnawse.bkt.clouddn.com/FsyJgSgROcPXOipFkfAPVQMe9wag)

我们观察到，一共250条数据，分成了10页显示。我们需要一页一页地把数据都爬下来。

使用ctrl+shift+I打开开发者工具，检查网页
![](http://plqfnawse.bkt.clouddn.com/Fq8olOx8xwYtp6tFtMiIfooM_aSf)

每一部电影都是被一个class="item"的div标签包裹。

#使用浏览器分析
选中这个节点，右键选择copy XPath
```
//*[@id="content"]/div/div[1]/ol/li[1]/div
```

如下图所示
![](http://plqfnawse.bkt.clouddn.com/Ft0X6yzYKtdtBPMOHV-5lgbh7uXe)

在开发者工具中使用快捷键ctrl+F,打开搜索框，

（Google chrome支持XPath搜索。）

我们将刚刚复制的XPath输入到搜索框中

可以看到，这个页面一共搜索到1条记录。
![](http://plqfnawse.bkt.clouddn.com/Fmwn_6Rs38Y4Rq7uXQGKVMn8A5q6)

我们将XPath修改一下
```
//*[@id="content"]/div/div[1]/ol/li/div
```
可以得到25条结果。

但是，这样的XPath是不好用的。

我们在快速查看页面元素的时候可以选择这样做。实际项目中，还是推荐手写XPath。

#使用scrapy shell测试
根据我们的需求，我想要爬取到电影的名称，链接，评分和电影中的名句
我发现这些信息都被class='info'的div包裹着。
![](http://plqfnawse.bkt.clouddn.com/FrXdu0knQ7_NYnwKZKayHWuUtToQ)
可以使用下面的XPath来提取我们需要的全部电影信息
```
//div[@class='info']
```
使用scrapy shell来进行一下测试，在你的终端输入如下命令：前提是你已经下载了scrapy.

```
scrapy shell https://movie.douban.com/top250
```
返回一大串信息：
![](http://plqfnawse.bkt.clouddn.com/Fqx4S3URjQK78svxTgfutyrgb9Jf)
输入response，结果返回的是403，说明被豆瓣拒绝了。输入quit命令退出之后，再输入下面的命令

```
scrapy shell https://movie.douban.com/top250 -s USER_AGENT='Mozilla/5.0'
```
这次成功返回200.

根据提示，我们输入view(response)
![](http://plqfnawse.bkt.clouddn.com/FnN9GNPlPCtW60RLymLfNh1m_2sB)

view(response)会将获取到的页面使用html默认软件打开，观察我们拿到的数据和原始网页是否相同。

接下来，尝试获取电影名

按enter键继续下面的工作。

![](http://plqfnawse.bkt.clouddn.com/FmtzXn0Yqps7BV_86iZ5NptPjklS)
我们输入response后按tab键会提示如上提示。

完整的命令是：
```
response.xpath("//div[@class='info']")
```
结果如下
![](http://plqfnawse.bkt.clouddn.com/Fho8vs37O3rZV29Cg_PoscfUoERQ)
是一个selector列表，我们先拿第一条电影名称的话，可以输入下面的命令
```
response.xpath("//div[@class='info']/div/a/span")[0].extract()
```
结果如下：
![](http://plqfnawse.bkt.clouddn.com/FiWBcTaN_EtMB8EAhJMV1AUKWcrU)
输出的内容还包含着<span>节点，而我们真正想要的是“肖申克的救赎”这几个字，很简单
```
response.xpath("//div[@class='info']/div/a/span/text()")[0].extract()
```
使用text()方法可以拿到<span>节点的内容。

同样的方法，我们可以拿到电影url，评分，quote。

```
response.xpath("//div[@class='info']/div/a/@href")[0].extract()
response.xpath('//div[@class="info"]/div[@class="bd"]/div[@class="star"]/span[@class="rating_num"]/text()')[0].extract()
response.xpath('//div[@class="info"]/div[@class="bd"]/p/span[@class="inq"]/text()')[0].extract()
```

对涉及到的XPath语法不熟悉的同学，可以到w3school自行补课。

#开始今天的项目
```
scrapy startproject douban_scrapy 
```
使用idea打开项目
首先在items.py中定义需要的数据。
```
# define the fields for your item here like:
movie_name = scrapy.Field()
movie_url = scrapy.Field()
star = scrapy.Field()
quote = scrapy.Field()
```
在spiders目录下创建Top250Spider.py。

在这个文件中需要导入的包有：
```
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.spiders import Rule, CrawlSpider

from douban_scrapy.items import DoubanScrapyItem
```
我们需要定义spider的名称，允许爬取的domain，start_urls。
```
    name = "top250spider"

    download_delay = 1

    allowed_domains = []

    start_urls = [
        'https://movie.douban.com/top250?start=0&filter='
    ]
```
前面忘记提一点，我们要观察每个页面的url的特点，以便确定下面的提取规则。
```
# 多页爬取规则
    rules = (
        Rule(LinkExtractor(allow=(r'\?start=\d+&filter=')), callback='parse_item',follow=True),
    )
```
使用parse_item方法处理item
```
def parse_item(self, response):
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
```
关于quote说明
```
if quote:
   quote = quote[0]
else:
   quote = ''
```
我发现页面中有些电影是没有提供quote的，需要特殊处理一下。

# pipelines.py
我打算将数据导入mongo，引入pymongo
```
import pymongo
```
重写__init__方法，在这里创建mongo连接，不需要事先创建database和collection，运行时会自动创建。
```
# 建立MongoDB数据库连接
client = pymongo.MongoClient('127.0.0.1', 27017)
# 连接所需数据库
db = client['douban']
# 连接所用集合，也就是我们通常所说的表
self.post = db['top250']
```
在process_item方法中，插入数据到mongo。
```
postItem = dict(item)  # 把item转化成字典形式
self.post.insert(postItem)  # 向数据库插入一条记录
return item
```
最后，将settings中的这段代码注释放开：
![](http://plqfnawse.bkt.clouddn.com/Fs_uerkGI4PxASJbrua6t9waHr3z)

并添加USER_AGENT，防止我们的请求被网站拒绝

运行爬虫
到项目路径下，执行下面的命令，数据就跑到你的mongo数据库里了，
```
~/python_work/douban_scrapy(master*) » scrapy crawl top250spider 
```

去检查一下mongo吧
![](http://plqfnawse.bkt.clouddn.com/FnfhLse-eCC7SyOwojSJkwwu4690)
```
{
    "_id": "5c4eddf90ffeb619de2774b2",
    "movie_name": "肖申克的救赎 / The Shawshank Redemption / 月黑高飞(港)  /  刺激1995(台)",
    "movie_url": "https://movie.douban.com/subject/1292052/",
    "star": "9.6",
    "quote": "希"
}
```
这正是我想要的数据。
完整代码已上传至github:
完。

