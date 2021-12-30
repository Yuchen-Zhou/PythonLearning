# 5.1使用说明
需要说明的是，Scrapy已经提供了许多Downloader Middleware，比如负责失败重试、自动重定向等功能的Downloader Middleware，它们被`DOWNLOADER_MIDDLEWARES_BASE`变量所定义  
DOWNLOADER_MIDDLEWARES_BASE变量的内容如下  
```python
{
    "scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware":100,
    "scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware":300,
    "scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware":350,
    "scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware":400,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware":500,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware":550,
    "scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware":560,
    "scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware":580,
    "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware":590,
    "scrapy.downloadermiddlewares.redirect.RedirectMiddleware":600,
    "scrapy.downloadermiddlewares.cookies.CookiesMiddleware":700, 
    "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware":750, 
    "scrapy.downloadermiddlewares.stats.DownloaderStats": 850,
    "scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware": 900
}
```
这是