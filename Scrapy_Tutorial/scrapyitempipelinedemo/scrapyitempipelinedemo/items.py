import scrapy

class MovieItem(scrapy.Item):
    name = scrapy.Field()
    categories = scrapy.Field()
    score = scrapy.Field()
    drama = scrapy.Field()
    directors = scrapy.Field()
    actors = scrapy.Field()

