import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from justcallhome.items import Article


class justcallhomeSpider(scrapy.Spider):
    name = 'justcallhome'
    start_urls = ['https://www.justcallhome.com/blog']

    def parse(self, response):
        links = response.xpath('//a[@class="read-more"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@title="Go to next page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//small/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="blog-meta"]/p/text()[2]').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="blog-body"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
