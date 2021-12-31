import pymongo
from scrapyitempipelinedemo.items import MovieItem
from elasticsearch import Elasticsearch
from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagePipeline

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