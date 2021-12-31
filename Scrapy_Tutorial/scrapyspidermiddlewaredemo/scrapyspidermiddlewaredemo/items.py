import scrapy

class DemoItem(scrapy.Item):
    origin = scrapy.Field()
    headers = scrapy.Field()
    args = scrapy.Field()
    url = scrapy.Field()