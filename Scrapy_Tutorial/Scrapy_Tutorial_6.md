# 7.1核心方法
我们可以自定义Item Pipeline，只需要实现指定的方法就好，其中必须实现的一个方法是：
- process_item(item, spider)

另外还有几个比较实用的方法，它们分别是：
- open_spider(spider)
- close_spider(spider)
- from_crawler(cls, crawler)

下面我们对这几个方法的用法进行详细介绍：
- process_item(item, spider)  
process_item是必须实现的方法，被定义的Item Pipeline会默认调用这个方法对Item进行处理，比如进行数据处理或将数据写入数据库等操作。process_item方法必须返回Item类型的值或者抛出一个DropItem异常

    process_item方法的参数有两个
    - item：Item对象，即被处理的Item
    - spider：Spider对象，即生成该Item的Spider

    该方法的返回类型如下
    - 如果返回的是Item对象，那么此Item会接着被低优先级的Item Pipeline的process_item方法处理，直到所有的方法被调用完毕
    - 如果抛出DropItem异常，那么此Item就会被抛弃，不再进行处理

- open_spider(spider)  
open_spider方法是在Spider开启的时候被自动调用的，在这里我们可以做一些初始化工作，如开启数据库连接等。其中参数spider就是被关闭的Spider对象

- close_spider(spider)  
close_spider方法是在一个类方法，用@classmethod标识，它接收一个参数crawler。通过crawler对象，我们可以拿到Scrapy的所有核心组件，如全局配置的每个信息。然后可以在这个方法里面创建一个Pipeline实例。参数cls就是Class，最后返回一个Class实例。

# 7.2目标
我们要爬取的目标网站是https://ssr1.scrape.center/，我们需要把每部电影的名称、类别、评分、简介、导演、演员的信息以及相关图片爬取下来，同时把每部电影的导演、演员的相关图片保存成一个文件夹，并将每步电影的完整数据保存到MongoDB和Elasticsearch里

这里使用Scrapy来实现这个电影数据爬虫，主要是为了了解Item Pipeline的用法。我们会使用Item Pipeline分别实现MongoDB存储、Elasticsearch存储、Image图片存储这三个Pipeline。

在开始前，请确保安装好MongoDB和Elasticsearch，另外安装好Python和PyMongo、Elasticsearch、Scrapy，参考如下：
- Scrapy:https://setup.scrape.center/scrapy
- MongoDB:https://setup.scrape.center/mongodb
- PyMongo:https://setup.scrape.center/pymongo
- Elasticsearch:https://setup.scrape.center/elasticsearch
- Elasticsearch Python包:https://setup.scrape.center/elasticsearch-py

# 7.3实战
首先新建一个项目，我们取名为scrapyitempipelinedemo,命令如下  
`scrapy startproject scrapyitempipelinedemo`  
接下来，我们创建一个Spider，命令如下  
`scrapy genspider scrape ssr1.scrape.center`  
这样我们就成功创建了一个Spider，名字为scrape，允许爬取的域名为`ssr1.scrape.center`。实现start_requests方法的代码如下：
```python
from scrapy import Request, Spider

class ScrapeSpider(Spider):
    name = 'scrape'
    allowed_domains = ['ssr1.scrape.center']
    start_url = 'http://ssr1.scrape.center/'
    max_page = 10

    def start_requests(self):
        for i in range(1, self.max_page):
            url = f'{self.base_url}/page/{i}'
            yield Request(url, callback=self.parse_index)

    def parse_index(self, response):
        print(response)
```

在这里我们声明了max_page即最大翻页数量，然后实现了start_requests方法，构造了10个初始请求分别爬取每个列表页，Request对应的回调方法修改为了parse_index，然后我们暂时在parse_index方法里面打印输出了response对象。

`scrapy crawl scrape`

运行结果如下

<img src='../pics/scrapy-18.png' width='80%'>

可以看到队对应的列表页的数据就被爬取下来了，Response的状态码为200.
接着我们可以在parse_index方法里面对response的内容进行解析，提取每部电影的详情页链接，通过审查源代码可以发现，其标题对应的CSS选择器为.item .name，如下图所示

<img src='../pics/scrapy-19.png' width='80%'>

所以这里我们可以借助response的css方法进行提取，提取链接之后生成详情页的Request。可以把parse_index方法改写如下：
```python
def parse_index(self, response):
        for item in response.css('.item'):
            href = item.css('.name::attr(href)').extract_first()
            url = response.urljoin(href)
            yield Request(url, callback=self.parse_detail)

    def parse_detail(self, response):
        print(response)
```

在这里我们首先筛选出了每部电影对应的节点，即`.item`，然后遍历这些节点提取其中`.name`选择器对应的详情链接，接着通过response的urljoin方法拼接成完整的详情页URL，最后构造新的详情页Request，回调方法设置为parse_detail，同时在parse_detail方法里面打印输出response。

重新运行，我们可以看到详情页的内容就被爬取下来了，如下图所示  
<img src='../pics/scrapy-20.png' width='80%'>

其实现在parse_detail里面的response就是详情页的内容了，我们可以进一步对详情页的内容进行解析，提取每部电影的名称、类别、评分、简介、导演、演员等信息。

首先我们新建一个Item，叫做MovieItem
```python
import scrapy

class MovieItem(scrapy.Item):
    name = scrapy.Field()
    categories = scrapy.Field()
    score = scrapy.Field()
    drama = scrapy.Field()
    directors = scrapy.Field()
    actors = scrapy.Field()
```

这里我们定义的几个字段name、categories、score、drama、directors、actors分别代表电影名称、类别、评分、简介、导演、演员。接下来我们就可以提取详情页了

```python
def parse_detail(self, response):
        item = MovieItem()
        item['name'] = response.xpath('//div[contains(@class, "item")]//h2/text()').extract_first()
        item['categories'] = response.xpath('//button[contains(@class, "category")]/span/text()').extract()
        item['score'] = response.css('.score::text').re_first('[\d\.]+')
        item['drama'] = response.css('.drama p::text').extract_first().strip()       
        item['directors'] = []
        directors = response.xpath('//div[contains(@class, "directors")]//div[contains(@class, "director")]')
        for director in directors:
            director_image = director.xpath('.//img[@class="image"]/@src').extract_first()
            director_name = director.xpath('.//p[contains(@class, "name")]/text()').extract_first()
            item['directors'].append({
                'name': director_name,
                'iamge': director_image
            })
        item['actors'] = []
        actors = response.css('.actors .actor')
        for actor in actors:
            actor_image = actor.css('.actor .image::attr(src)').extract_first()
            actor_name = actor.css('.actor .name::text').extract_first()
            item['actors'].append({
                'name': actor_name,
                'image': actor_image
            })
            yield item
```

在这里我们首先创建了一个MovieItem对象，赋值为Item，然后我们使用xpath方法提取了name，categories两个字段。然后用css选择器提取了score和drama字段，同时score字段最后还调用了re_first方法传入正则表达式提取分数的内容。对于导演directors和演员actors，我们首先提取了单个director和actor节点，然后分别从中提取了姓名和照片，最后组成一个列表赋值给directors和actors字段

重新运行，结果如下

<img src='../pics/scrapy-21.png' width='80%'>

可以看到这里我们已经成功提取了各个字段然后生成了MovieItem对象了

- MongoDB  
首先确保MongoDB已经安装并且正常运行，既可以运行在本地，也可以运行在远程，我们需要把它的连接字符串构造好，连接字符串的格式如下:
`mongodb://[username:password@]host1[:port1][,...hostN[:portN]][/[defaultauthdb][?options]]`

    比如运行在本地27017端口的无密码的MongoDB可以直接写为：  
    `mongodb://localhost:27017`

    如果是远程的MongoDB，可以是根据用户名、密码、地址、端口等构造。  
    我们实现了一个MongoDBPipeline，将信息保存到MongoDB，在pipelines.py里添加如下类的实现：
    ```python
    import pymongo
    from scrapyitempipelinedemo.items import MovieItem

    class MongoDBPipeline(object):

        @classmethod
        def from_crawler(cls, crawler):
            cls.connection_string = crawler.settings.get('MONGODB_CONNECTION_STRING')
            cls.database = crawler.settings.get('MONGODB_DATABASE')
            cls.collection = crawler.settings.get('MONGODB_COLLECTION')
            return cls

        def open_spider(self, spider):
            self.client = pymongo.MongoClient(self.connection_string)
            self.db = self.client[self.database]

        def process_item(self, item, spider):
            self.db[self.database].update_one({
                'name': item['name']
            }, {
                '$set': dict(item)
            }, True)
            return item

        def close_spider(self, spider):
            self.client.close()
    ```

    这里我们首先利用了from_crawler获取里全局配置MONGODB_CONNECTTION_STRING、MONGODB_DATABASE和MONGODB_COLLECTION，即MongoDB连接字符串、数据库名称、集合名词，然后将三者赋值为类属性。

    接着我们实现了open_spider方法，该方法就是利用from_crawler赋值的connection_string创建一个MongoDB连接对象，然后声明数据库操作对象，close_spider则是在Spider运行结束时关闭MongoDB连接。

    接着最重要的就是process_item方法了，这个方法接收的参数item就是从Spider生成的item对象，该方法需要将此Item存储到MongoDB中。这里我们使用了update_one方法实现了存在即更新，不存在则插入到功能。

    接下来我们需要在settings.py里添加MONGODB_CONNECTION_STRING、MONGODB_DATABASE和MONGODB_COLLECTION这3个变量，相关代码如下：
    ```python
    ITEM_PIPELINES = {
    'scrapyitempipelinedemo.pipelines.MongoDBPipeline': 300,
    }
    MONGODB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')
    MONGODB_DATABASE = 'movies'
    MONGODB_COLLECTION = 'movies'
    ```

    这里可以将MONGODB_CONNECTION_STRING设置为从环境变量中读取，而不用将明文密码等信息写到代码里

    如果是本地无密码的MongoDB，直接写为如下内容就可  
    `MONGODB_CONNECTION_STRING = 'mongodb://localhost:27017' # or just use 'localhost'`
    这样，一个保存到MongoDB的Pipeline就创建好了，利用process_item方法我们即可完成数据插入到MongoDB的操作，最后会返回Item对象

- Elasticsearch  
存储到Elasticsearch也是一样，我们需要先创建一个Pipeline，代码如下
```python
from elasticsearch import Elasticsearch

class ElasticsearchPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        cls.connection_string = crawler.settings.get('ELASTICSEARCH_CONNECTION_STRING')
        cls.index = crawler.settings.get('ELASTICSEARCH_INDEX')
        return cls()

    def open_spider(self, spider):
        self.conn = Elasticsearch([self.connection_string])
        if not self.conn.indices.exists(self.index):
            self.conn.indices.exists(self.index)

    def process_item(self, item, spider):
        self.conn.index(index=self.index, body=dict(item), id=hash(item['name']))
        return item

    def close_spider(self, spider):
        self.conn.transport.close()
```

这里同样定义了ELASTICSEARCH_CONNECTION_STRING代表Elasricsearch的连接字符串，ELASTICSEARCH_INDEX代表索引名称，具体初始化的操作和MongoDBPipeline的原理是类似的

在process_item方法中，我们调用了index方法对数据进行索引，我们指定了3个参数，第一个参数index代表索引名称，第二个参数body代表数据对象，在这里我们将Item转为了字典类型，第三个参数id则是索引数据的id，这里我们直接使用电影名称的hash值作为id，或者自行指定其他id也可以的。

同样地，我们需要在settins.py里面添加ELASTICSEARCH_CONNECTION_STRING和ELASTICSEARCH_INDEX：
```python
ELASTICSEARCH_CONNECTION_STRING = os.getenv('ELASTICSEARCH_CONNECTION_STRING')
ELASTICSEARCH_INDEX = 'movies'
```
这里的ELASTICSEARCH_CONNECTION_STRING同样是从环境变量中读取的，他的格式如下：
`http[s]://[username:password@]host[:port]`

比如我实际使用的ELASTICSEARCH_CONNECTION_STRING值就类似：  
`https://user:password@...:9200`

这里可以连接你的，这样ElasticsearchPipeline就完成了




- Image Pipeline  
Scrapy提供了专门处理下载的Pipeline，包括文件下载和图片下载。下载文件和图片的原理与抓取页面的原理一样，因此下载过程支持异步和多线程，十分高效,[参考链接](https://docs.scrapy.org/en/latest/topics/media-pipeline.html)

    首先定义存储文件的路径，需要定义一个IMAGES_STORE变量，在settings.py中添加如下代码：  
    `IMAGES_STORE = './images'`

    在这里我们将路径定义为当前路径下的iamges子文件夹，即下载的图片都会保存到本项目的images文件夹中。  
    内置的ImagesPipeline会默认读取Item的image_urls字段，并认为它是列表形式，接着遍历该字段后取出每个URL进行图片下载。   
    但是现场生成的Item的图片链接字段并不是images_urls字段表示的，我们是想下载directors和actors的每张图片。所以为了实现下载，我们需要重新定义下载的部分逻辑，即自定义ImagePipeline继承内置的ImagesPipeline，重写几个方法。  
    
    我们定义的ImagePipeline代码如下：
    ```python
    from scrapy import Request
    from scrapy.exceptions import DropItem
    from scrapy.pipelines.images import ImagePipeline
    
    class ImagePipeline(ImagePipeline):

        def file_path(self, request, response=None, info=None):
            movie = request.meta['movie']
            type = request.meta['type']
            name = request.meta['name']
            file_name = f'{movie}/{type}/{name}.jpg'
            return file_name

        def item_completed(self, results, item, info):
            image_paths = [x['path'] for ok, x in results if ok]
            if not image_paths:
                raise DropItem('Image Download Failed')

        def get_media_requests(self, item, info):
            for director in item['directors']:
                director_name = director['name']
                director_iamge = director['image']
                yield Request(director_iamge, meta={
                    'name': director_name,
                    'type': director,
                    'movie': item['name'],
                })

            for actor in item['actors']:
                actor_name = actor['name']
                actor_image = actor['image']
                yield Request(actor_image, meta={
                    'name': actor_name,
                    'type': 'actor',
                    'movie': item['name']
                })

    ```

    在这里我们实现了ImagePipeline，继承Scrapy内置的ImagePipeline，重写下面几个方法。

    - get_media_requests：第一个参数item是爬取生成的Item对象，我们需要下载的图片链接    
    - file_path：第一个参数request就是当前下载对应的Response对象。这个方法用来保存的文件名，在这里我们获取了刚才生成的Request的meta信息，包括movie（电影名称）、type（电影类型）和name（导演或演员姓名），最终三者拼合为file_name作为最终的图片路径
    - item_compeleted：单个Item完成下载时的处理方法，因为并不是每张访问