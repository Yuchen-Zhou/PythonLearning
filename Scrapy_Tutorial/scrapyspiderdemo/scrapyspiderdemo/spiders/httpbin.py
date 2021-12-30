import scrapy
from scrapy.http import FormRequest, JsonRequest


class HttpbinSpider(scrapy.Spider):
    name = 'httpbin'
    allowed_domains = ['www.httpbin.org']
    start_url = 'http://www.httpbin.org/post'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36\
             (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    data = {'name': 'germey', 'age': '26'}

    def start_requests(self):
        yield FormRequest(self.start_url, callback=self.parse_response,
                formdata=self.data)
        yield JsonRequest(self.start_url, callback=self.parse_response,
                data=self.data)

    def parse_response(self, response):
        print('text', response.text)


