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

这里我们可以看到几个Request对应的Response的内容被输出了，每个返回结果带有args参数，query为0-4 
另外我们可以定义一个Item，4个字段就是目标站点返回的字段，相关代码:
```python
import scrapy

class DemoItem(scrapy.Item):
    origin = scrapy.Field()
    headers = scrapy.Field()
    args = scrapy.Field()
    url = scrapy.Field()
```
可以在parse方法中将返回的Response的内容转化为DemoItem，将parse方法做如下修改：
```python
def parse(self, response):
        item = DemoItem(**response.json())
        yield item
```

重新运行，最终Spider就会产生对应的DemoItem了，运行效果如下：

<img src='../pics/scrapy-15.png' width='80%'>

可以看到原本Response的JSON数据就被转化为了DemoItem并返回。  
接下来在middlewares.py中重新声明一个CustomizeMiddleware类，内容如下：
```python
class CustomizeMiddleware(object):
    def process_start_requests(self, start_requests, spider):
        for request in start_requests:
            url = request.url
            url += '&name=germey'
            request = request.replace(url=url)
            yield request
```

这里实现了`process_start_requests`方法，它可以对start_requests表示的每个Request进行处理，我们首先获取了每个Request的URL，然后在URL的后面又拼接上了另一个Query参数，name等于germey，然后我们利用request的replace方法将url属性替换，这样就成功为Request赋值了新的URL。

接着我们需要将此CustomizeMiddleware开启，在settings.py中进行如下的定义：
```
SPIDER_MIDDLEWARES = {
    'scrapyspidermiddlewaredemo.middlewares.CustomizeMiddleware' : 543,
}
```
这样我们就开启了CustomizeMiddleware这Spider Middleware。  
重新运行Spider，这时候我们可以看到输出结果就变成了下面这样
<img src='../pics/scrapy-16.png' width='80%'>

可以观察到url属性成功添加了`name=germey`的内容，这说明我们利用Spider Middleware成功改写Request。  
除了改写start_requests，我们还可以对Response和Item进行改写，比如对Response进行改写，我们可以尝试更改其状态码，在CustomizeMiddleware里面增加如下定义：
```python
def process_spider_input(self, response, spider):
        response.status = 201
    
    def process_spider_output(self, response, result, spider):
        for i in result:
            if isinstance(i, DemoItem):
                i['origin'] = None
                yield i
```

这里定义了process_spider_input和process_spider_output方法，分别来处理Spider的输入和输出。对于process_spider_input方法来说，输入自然就是Response对象，所以第一个参数就是response，我们在这里直接修改了状态码。对于process_spider_output方法来说，输出就是Response或Item了，但是这里二者是混合在一起的，作为result参数传递过来。result是一个可迭代对象，我们遍历了result，然后判断了每个元素的类型，在这里使用isinstance方法进行判定：如果i是DemoItem类型，就把它的origin属性设置为空。当然这里还可以针对Request类型做类似的处理。

另外在parse方法里添加Response的状态码的输出结果
```python
print('Status:', response.status)
```
重新运行Spider，结果如下

<img src='../pics/scrapy-17.png' width='80%'>

在Scrapy中，还有几个内置的Spider Middleware
- **HttpErrorMiddleware**  
HttpErrorMiddleware的主要作用是过滤我们需要忽略的Response，比如状态码为200-299就直接返回，50以上的就不会处理

    ```python
    def __init__(self, settings):
        self.handle_httpstatus_all = settings.getbool('HTTPERROR_ALLOW_ALL')
        self.handle_httpstatus_list = settings.getlist('HTTPERROR_ALLOWED_CODES')

    def process_spider_input(self, response, spider):
        if 200 <= response.status < 300:
            return
        meta = response.meta
        if 'handle_httpstatus_all' in meta:
            return 
        if 'handle_httpstatus_list' in meta:
            allowed_status = meta['handle_httpstatus_list']
        elif self.handle_httpstatus_all:
            return
        else:
            allowed_statuses = getattr(spider, 'handle_httpstatus_list', self.handle_httpstatus_list)
        if response.status in allowed_statuses:
            return 
        raise HttpError(response, 'Ignoring non-200 response')
    ```
可以看到它实现了process_spider_input方法，然后判断了状态码200～299就直接返回，否则会根据handle_httpstatus_all和handle_httpstatus_list来进行处理。例如状态码在handle_httpstatus_list定义的范围内，就会直接处理，否则抛出HttpError异常。这也解释了为什么刚才我们把Response的状态码修改为201却依然能被正常处理的原因，如果我们修改为非200～299的状态码，就会抛出异常了

另外，如果想要针对一些错误类型的状态码进行处理，可以修改Spider的handle_httpstatus_list属性，也可以修改Request meta的handle_httpstatus_list属性，还可以修改全局settings HTTPERROR_ALLOWED_CODES。  
比如我们想要处理404状态码，可以进行如下配置：
`HTTPERROR_ALLOWED_CODES = [404]`

- **OffsiteMiddleware**  
OffsiteMiddleware的主要作用是过滤不符合allowded_domains的Request，Spider里面定义的allowed_domains其实就是在这个Spider Middleware里生效的。其核心代码实现如下：
```python
def process_spider_output(self, response, result, spider):
    for x in result:
        if isinstance(x, Request):
            if x.dont_filter or self.should_follow(x, spider):
                yield x
            else:
                domain = urlparse_cached(x).hostname
                if domain and domain not in self.domains_seen:
                    self.domains_seen.add(domain)
                    logger.debug(
                        "Filtered offsite request to %(domain)r : %(request)s",
                        {'domain': domain, 'request': x}, extra={'spider': spider})
                    self.stats.inc_value('offsite/domains', spider=spider)
                self.stats.inc_value('offsite/filtered', spider=spider)
        else:
            yield x
```

可以看到，这里首先遍历了result，然后判断了Request类型的元素赋值为x。然后根据x的dont_filter、url和Spider的allowed_domains进行了过滤，如果不符合allowed_domains，就直接输出日志并不再返回Request，只有符合要求的Request才会被返回并继续调用

- **UrlLengthMiddleware**  
UrlLengthMiddleware的主要作用是根据Request的URL长度对Request进行过滤，如果URL的长度过长，此Request就会被忽略。

    ```python
    @classmethod 
    def from_settings(cls, settings):
        maxlength = settings.getint('URLLENGTH_LIMIT')
    
    def process_spider_output(self, response, result, spider):
        def _filter(request):
            if isinstance(request, Request) and len(request.url) > self.maxlength:
                logger.debug("Ignoring link (url length > %(maxlength)d: %(url)s) ", extra={'spider': spider})
                return False
            else:
                return True

            return (r for r in result or () if _filter(r))
    ```

可以看到，这里利用了process_spider_output对result里面的Request进行过滤，如果是Request类型并且URL长度超过了最大限制，就会被过滤。我们可以从中了解到，如果想要根据URL的长度进行过滤，可以设置URLLENGTH_LIMIT   
比如我们只想爬取URL长度小于50的页面，那么就可以进行如下配置：  
`URLLENGTH_LIMIT = 50`

可见Spider Middleware能够非常灵活地对Spider的输入和输出进行处理，内置的一些Spider Middleware在某些场景下也发挥了重要作用。
