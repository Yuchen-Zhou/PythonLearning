from scrapy import Selector
body = '<html><head><title>Hello World</title></head></html>'
selector = Selector(text=body)
title = selector.xpath('//title/text()').extract_first()
print(title)