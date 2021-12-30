# 6.1使用说明
同样需要说明的是，Scrapy其实已经提供了许多Spider Middleware，与Downloader Middleware类似，它们被SPIDER_MIDDLEWARES_BASE变量所定义。

SPIDER_MIDDLEWARES_BASE变量的内容如下：
```python
{
    'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': 50,
    'scrapy.spidermiddlewares.offset.OffsetMiddleware': 500,
    'scrapy.spidermiddlewares.referer.RefererMiddleware': 700,
    'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': 800,
    'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
}
```
SPIDER_MIDDLEWARES_BASE里面定义的Spider Middleware是默认生效的，如果我们要自定义SPider Middleware，可以和Downloader Middleware一样，创建Spider Middleware并将其加入SPIDER_MIDDLEWARES。直接修改这个变量就可以添加自己定义的Spider Middleware。以及禁用SPIDER_MIDDLEWARES_BASE里面定义的Spider Middleware

# 6.2核心方法
Scrapy内置的Spider Middleware为Scrapy提供了基础的功能。如果我们想要扩展其功能，只需要实现几个方法。
每个Spider Middleware都定义了以下一个或多个方法的类，核心方法有如下4个。
- process_spider_input(response, spider)
- process_spider_output(response, result, spider)
- process_spider_exception(response, exception, spider)
- process_start_request(start_requests, spider)

只需要实现其中一个方法就可以定义一个Spider Middleware。下面我们看看这4个方法的详细用法。

- process_spider_input(response, spider)  
当Response通过Spider Middleware时，process_spider_input方法被调用，处理该Response。他有两个参数
    - response：Response对象，即被处理的Response
    - spider：Spider对象，即该Response对应的Spider对象

process_spider_input应该返回None或者抛出异常。
    - 如果它返回None，Scrapy会继续处理该Response，调用所有其他的Spider Middleware直到Spider处理该Response  
    - 如果它抛出一个异常，Scrapy不会调用任何其他Spider Middleware的process_spider_input方法，并调用Request的errback方法。errback的输出将会以另一个方向重新输入中间件，使用process_spider_output方法来处理，当其抛出异常时则调用process_spider_exception来处理


- process_spider_output(response, result, spider)  
当Spider处理Response返回结果时，process_spider_output方法被调用。他有3个参数
    - response：Response对象，即生成该输出的Response
    - result：包含Request或Item对象的可迭代对象，即Spider返回的结果
    - spider：Spider对象，即结果对应的Spider对象

process_spider_output必须返回包含Request或Item对象的可迭代对象

- process_spider_exception(response, exception, spider)  
当Spider或Spider Middleware的process_spider_input方法抛出异常时，process_spider_exception方法被调用。它有3个参数。
    - response：Response对象，被抛出的异常
    - exception：Exception对象，被抛出的异常
    - spider：Spider对象，即抛出该异常的Spider对象

process_spider_exception必须返回None或者一个（包含Response或Item对象的）可迭代对象。
    - 如果它返回None，那么Scrapy将继续处理该异常，调用其他Spider Middleware中的process_spider_exception方法，直到所有Spider Middleware都被调用。
    - 如果它返回一个可迭代对象，则其他Spider Middleware的process_spider_output方法被调用，其他的process_spider_exception不会被调用

- process_start_request(start_requests, spider)  
process_start_requests方法以Spider启动的Request为参数被调用，执行的过程类似于process_spider_output，只不过它没有相关联的Response并且必须返回Request。
    - start_requests：包含Request的可迭代对象，即StartRequests。
    - spider：Spider对象，即Start Requests所属的Spider

process_start_requests方法必须返回另一个包含Request对象的可迭代对象

# 6.3实战
首先我们新建一个Scrapy项目叫做scrapyspidermiddlewaredemo  
`scrapy startproject scrapyspidermiddlewaredemo`
然后新建一个Spider  
`scrapy genspider httpbin www.httpbin.org`

进入httpbin.py修改Spider
```python
from scrapy import Request, Spider

class HttpbinSpider(scrapy.Spider):
    name = 'httpbin'
    allowed_domains = ['www.httpbin.org']
    start_url = 'http://www.httpbin.org/get'

    def start_requests(self, response):
        for i in range(5):
            url = f'{self.start_url}?query={i}'
            yield Request(url, callback=self.parse)

    def parse(self, response):
        print(response.text)
```
运行代码`scrapy crawl httpbin`

<img src='../pics/scrapy-14.png' width='80%'>
