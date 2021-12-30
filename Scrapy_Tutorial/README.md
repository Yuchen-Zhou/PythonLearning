# Scrapy框架教程
Scrapy是一个基于Python开发的爬虫框架，该框架提供了非常多的爬虫相关的基础组件，架构清晰，可扩展性极强。基于Scrapy，我们灵活高效地完成各种爬虫需求

## 1.[Scrapy介绍](./Scrapy_Tutorial_1.md)
本节介绍了Scrapy框架的基本架构、数据流过程以及项目结构

## 2.[Scrapy入门](./Scrapy_Tutorial_2.md)
通过Scrapy官方推荐的教程，完成了第一个Scrapy爬虫，输出并写入了MongoDB数据库

## 3.[Selector的使用](./Scrapy_Tutorial_3.md)
Selector是基于parcel库构建的，依赖于lxml，支持XPath选择器、CSS选择器以及正则表达式，功能全面，解析速度和准确度非常高


## 4.[Spider的使用](./Scrapy_Tutorial_4.md)
在Scrapy中，网站的链接配置、抓取逻辑、解析逻辑其实都是在Spider中配置的。

## 5.[Downloader Middleware的使用](./Scrapy_Tutorial_5.md)
Downloader Middleware即下载中间件。它是处于Scrapy的Engine和Downloader之间的处理模块。在Engine把从Scheduler获取的Request发送给Downloader的过程中，以及Downloader把Response发送回Engine的过程中，Request和Response都会经过Downloader Middleware的处理。

也就是说，Downloader Middleware在整个架构中起作用的位置是以下两个：
- Engine从Scheduler获取Request发送给Downloader，在Request被Engine发送给Downloader执行下载之前，Downloader Middleware可以对Request进行修改
- Downloader执行Request后生成Response，在Response被Engine发送给Spider之前，也就是在Response被Spider解析之前，Downloader Middleware可以对Response进行修改


## 6.[Spider Middleware的使用](./Scrapy_Tutorial_5.md)
Spider Middleware是处于Spider和Engine之间的处理模块。当Downloader生成Response之后，Response会被发送给Spider，在发送给Spider之前，Response会首先经过Spider Middleware的处理，当Spider处理生成Item和Request之后，Item和Request还会经过Spider Middleware的处理。

Spider Middleware有如下3个作用
- Downloader生成Response后，Engine会将其发送给Spider进行解析，在Response发送给Spider之前，可以借助Spider Middleware对Response进行处理
- Spider生成Request之后会被发送至Engine，然后Request会被转发到Scheduler，在Request被发送给Engine之前，可以借助Spider Middleware对Request进行处理。
- Spider生成Item之后会被发送至Engine，然后Item会被转发到Item Pipeline，在Item被发送Engine之前，可以借助Spider Middleware对Item进行处理