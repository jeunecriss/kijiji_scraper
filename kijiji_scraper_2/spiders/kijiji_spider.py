import scrapy
from kijiji_scraper_2.items import KijijiScraper2Item
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

class KijijiItemSpider(scrapy.Spider):

    name = 'kijiji'
    base_url = "https://www.kijiji.ca"
    page = 0
    max_pages = 2

    def start_requests(self):
        urls = [
            "https://www.kijiji.ca/b-appartement-condo/ville-de-quebec/c37l1700124?ad=offering"
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.results_page)

    def results_page(self, response):
        apartment_paths = response.css(".info-container a.title::attr(href)").extract()

        for path in apartment_paths:
            full_url = KijijiItemSpider.base_url + path
            yield scrapy.Request(url=full_url, callback=self.apartment_page)

        next_path = response.css('a[title~="Suivante"]::attr(href)').extract_first()

        if next_path and KijijiItemSpider.page < KijijiItemSpider.max_pages:
            KijijiItemSpider.iteration += 1
            next_url = KijijiItemSpider.base_url + next_path
            yield scrapy.Request(url=next_url, callback=self.results_page)

    def apartment_page(self, response):
        l = ItemLoader(item=KijijiScraper2Item(), response=response)
        l.default_output_processor = scrapy.loader.processors.TakeFirst()

        l.add_value("url", response.url)
        l.add_css("title", "title::text")
        l.add_css("price", 'span[class^="currentPrice"] > span::text')

        return l.load_item()