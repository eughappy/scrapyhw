import scrapy

from test_spyder.items import AuthorItem, QuoteItem

class GetQuotesSpider(scrapy.Spider):
    name = 'get_quotes'
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]

    def parse(self, response, **kwargs):
        for q in response.xpath("/html//div[@class='quote']"):
            quote = q.xpath("span[@class='text']/text()").get().strip()
            author = q.xpath("span/small[@class='author']/text()").get().strip()
            tags = q.xpath("div[@class = 'tags']/a/text()").extract()
            yield QuoteItem(quote = quote, author = author, tags = tags)
            yield response.follow(url = self.start_urls[0] + q.xpath("span/a/@href").get(), callback=self.parse_author)
            #print(tags)

        next_link = response.xpath("/html//li[@class = 'next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url = self.start_urls[0] + next_link)

    @classmethod
    def parse_author(cls, response, **kwargs):
        a = response.xpath("/html//div[@class = 'author-details']")
        fullname = a.xpath("h3[@class='author-title']/text()").get().strip()
        born_date = a.xpath("p/span[@class='author-born-date']/text()").get().strip()
        born_location = a.xpath("p/span[@class='author-born-location']/text()").get().strip()
        description = a.xpath("div[@class='author-description']/text()").get().strip()
        #print(fullname, '\t' ,born_date, born_location, '\n' , description)
        yield AuthorItem(fullname=fullname, born_date = born_date, born_location = born_location, description = description)
