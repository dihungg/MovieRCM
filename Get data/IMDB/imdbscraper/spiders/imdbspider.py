import scrapy
import json
from imdbscraper.items import Info


class ImdbspiderSpider(scrapy.Spider):
    name = "imdbspider"
    allowed_domains = ["imdb.com"]
    start_urls = ["https://m.imdb.com/chart/top/"]

    def parse(self, response):
        
        raw_data = response.css("script[id='__NEXT_DATA__']::text").get()

        json_data = json.loads(raw_data)

        needed_data = json_data['props']['pageProps']['pageData']['chartTitles']['edges']

        info = Info()

        for movie in needed_data:
            info['Title'] = movie['node']['titleText']['text'],
            info['imdbRating']  = movie['node']['ratingsSummary']['aggregateRating'],

            yield info