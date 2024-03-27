import scrapy
import json
from itemadapter import ItemAdapter
from scrapy import Item, Field
from scrapy.crawler import CrawlerProcess

class QuoteItem(Item):
    quote = Field()
    author = Field()
    description = Field()

class AuthorItem(Item):
    fullname = Field()
    born_date = Field()
    born_location = Field()
    description = Field()

class DataPipeLine:
    quotes = []
    author = []

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if 'fullname' in adapter.keys():
            self.author.append(dict(adapter))
        elif 'quote' in adapter.keys():
            self.quotes.append(dict(adapter))
        else:
            raise Exception('Problem!')
        
    def close_spider(self,spider):
        with open('quotes.json','w',encoding ='utf-8') as f:
            json.dump(self.quotes, f, ensure_ascii=False, indent=4)
        with open('authors.json','w',encoding ='utf-8') as f:
            json.dump(self.author, f, ensure_ascii=False, indent=4)

class QuotesSpider(scrapy.Spider):
    name = 'get_quotes'
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]
    custom_settings = {"ITEM_PIPELINES":{DataPipeLine:300}}

    def parse(self, response, **kwargs):
        for q in response.xpath("/html//div[@class='quote']"):
            quote = q.xpath("span[@class='text']/text()").get().strip()
            author = q.xpath("span/small[@class='author']/text()").get().strip()
            tags = q.xpath("div[@class = 'tags']/a/text()").extract()

            yield QuoteItem(quote = quote, author = author, tags = tags)
            yield response.follow(url = self.start_urls[0] + quote.xpath("span/a/@href").get(), callback=self.parse_author)
            #print(tags)

        next_link = response.xpath("/html//li[@class = 'next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url = self.start_urls[0] + next_link)

    @classmethod
    def parse_author(cls, response, **kwargs):
        a = response.xpath("/html//div[@class = 'author-details']")
        fullname = a.xpath("h3[@class='author-title']/text()").get().strip()
        born_date = a.xpath("h3[@class='author-born-date']/text()").get().strip()
        born_location = a.xpath("h3[@class='author-born-location']/text()").get().strip()
        description = a.xpath("h3[@class='author-description']/text()").get().strip()
        print(fullname, '\t' ,born_date, born_location, '\n' , description)

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.start()