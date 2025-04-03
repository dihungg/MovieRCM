import scrapy
import json
from ..items import RottenItem

class ImdbSpider(scrapy.Spider):
    name ='rotten'
    allowed_domains = ['www.rottentomatoes.com']
    start_urls = ["https://www.rottentomatoes.com/browse/movies_in_theaters/"]

    def parse(self, response):
        all_div = response.css("div[class='caption-wrap']")
        for div in all_div:
            information = RottenItem()
            information['title'] = div.css("span[class='p--small']::text").get()
            information['movie_rotten'] = div.css("rt-text[class='criticsScore']::text").get()
            information['aud_rating'] = div.css("rt-text[class='audienceScore']::text").get()

            yield information
