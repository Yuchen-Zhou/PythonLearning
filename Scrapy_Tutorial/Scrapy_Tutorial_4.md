# 4.1Spider运行流程
在实现Scrapy爬虫项目时，最核心的类便是Spider类了。他定义了如何爬取某个网站的流程和解析方式。简单来说，Spider就是要做如下两件事：
- 定义爬取网站的动作
- 分析爬取下来的网页 

对于Spider类来说，整个爬取循环如下所述。  
(1)以初始的URL初始化Request并设置回调方法。当该Request成功请求并返回时，将生成的Response并将其作为参数传给该回调方法  
(2)在回调方法内分析返回的网页内容。返回结果可以是有两种形式，一种是将解析到的有效结果返回字典或Item对象，下一步可直接保存或经过处理后保存；另一种是解析的下一个（如下一页）链接，可以利用此链接构造Request并设置新的回调放啊，返回Request  
(3)如果返回的是字典或Item对象，可通过Feed Exports等形式存入文件，如果设置了Pipeline，可以经由Pipeline处理（如过滤、修正等）并保存  
(4)如果返回的是Request，那么Request执行成功得到的Response之后会再次传递给Request中定义的回调方法，可以再次使用选择器来分析新得到的网页内容，并根据分析的数据生成Item  


# 4.2Spider类分析
我们定义的Spider继承自`scrapy.spiders.Spider`，即`scrapy.Spider`类，二者指代的是同一个类，这个类是最简单最基本的Spider类，其他的Spider必须继承这个类。  
这个类提供了`start_requests`方法的默认实现，读取并请求`start_urls`属性，然后根据返回的结果调用parse方法解析结果。另外它还有一些基础属性

- name：爬虫名称，是定义的Spider名字的字符串。Spider的名字定义了Scrapyard如何定位并初始化Spider，所以它必须是唯一的。不过我们可以生成多个相同的Spider实例，这个没有任何限制。name是Spider最重要的属性，而且是必须的。如果该Spider爬取单个网站，一个常见的做法是以该网站的域名名称来命名spider。例如Spider爬取mywebsite.com，该Spider就叫mywebsite。
- allowed_domain：允许爬取的域名，是一个可选的配置，不在此范围的链接不会被跟进爬取。
- start_urls：起始URL列表，当我们没有实现`start_requests`方法时，默认会从这个列表开始抓取
- custom_settings：一个字典，是专属于本Spider的配置，此设置会覆盖项目全局的设置，而且此设置必须在初始化前被更新，所以它必须定义成类变量。
- crawler：此属性是由`from_crawler`方法设置的，代表的是本Spider类对应的Crawler对象，Crawler对象中包含了很多项目组件，利用它我们可以获取项目的一些配置信息，常见的就是获取项目的设置信息，即Settings。
- settings：一个Settings对象，利用它我们可以直接获取项目的全局设置变量

除了一些基础属性，Spider还有一些常用的方法
- start_requests：此方法用于生成初始请求，它必须返回一个可迭代对象，此方法会默认使用start_urls里面的URL构造Request，而且Request是GET请求方式。
- parse：当Response没有指定回调方法时，该方法会被默认调用，他负责处理Response，并从中提取想要的数据和下一步的请求，然后返回。该方法需要返回一个包含Request或Item的可迭代对象
- closed：当Spider关闭时，该方法会被调用，这里一般会定义释放资源的一些操作或其他收尾操作

# 4.3实例演示
首先我们创建一个Scrapy项目  
`scrapy startproject scrapyspiderdemo`  
运行完毕之后，当前运行目录便出现了一个scrapyspiderdemo文件夹，即对应的Scrapy项目就创建成功了。  
接着我们进入demo文件夹，来针对www.httpbin.org这个网站创建一个Spider  
`scrapy genspider httpbin www.httpbin.org`  
这时候我们可以看到项目目录下生成了一个HttpbinSpider，内容如下
```python
import scrapy

class HttpbinSpider(scrapy.Spider):
    name = 'httpbin'
    allowed_domains = ['www.httpbin.org']
    start_urls = ['http://www.httpbin.org/']

    def parse(self, response):
        pass
```
这时候我们可以在parse方法中打印输出一些response对象的基础信息，同时修改`start_urls`为http://www.httpbin.org/，这个链接可以返回GET请求的一些详情信息，最终我们可以将Spider修改。
```python
import scrapy

class HttpbinSpider(scrapy.Spider):
    name = 'httpbin'
    allowed_domains = ['www.httpbin.org']
    start_urls = ['http://www.httpbin.org/get']

    def parse(self, response):
        print('url', response.url)
        print('request', response.request)
        print('status', response.status)
        print('headers', response.headers)
        print('text', response.text)
        print('meta', response.meta)
```
这里我们打印了response的多个属性。
- url：请求的页面URL，即Request URL
- request：response对应的request对象
- status：状态码，即Response Status Code
- text：响应体，即Response Body
- meta：一些附加信息，这些参数往往会附在meta属性里

运行结果如下
<img src='../pics/scrapy-10.png' width='80%'>

可以看到，这里分别打印出了`url、request、status、headers、text、meta`信息。
注意，这里没有显式地申明初始请求，是因为Spider默认为我们实现了一个`start_requests`方法  
```python
def start_requests(self):
    for url in self.start_urls:
        yield Request(url, dont_filter=True)
```
可以看到，逻辑就是读取`start_urls`然后生成Request，这里并没有为Request指定callback，默认就是parse方法。他是一个生成器，返回所有的Request加入调度队列。  
因此，如果我们想要自定义初始请求，就可以在Spider中重写`start_quests`方法，比如我们想自定义请求页面链接和回调方法，可以把`start_requests`方法修改为下面这样
```python

```

