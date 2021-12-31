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

```