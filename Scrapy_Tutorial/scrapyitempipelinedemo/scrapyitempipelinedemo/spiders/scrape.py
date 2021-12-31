import scrapy


class ScrapeSpider(scrapy.Spider):
    name = 'scrape'
    allowed_domains = ['ssr1.scrape.center']
    start_urls = ['http://ssr1.scrape.center/']

    def parse(self, response):
        pass
