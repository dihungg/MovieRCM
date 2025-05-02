import scrapy
import json
from rotten.items import RottenItem


class RottenSpider(scrapy.Spider):
    name = "rotten"
    allowed_domains = ["editorial.rottentomatoes.com"]
    start_urls = [
        "https://editorial.rottentomatoes.com/guide/best-movies-of-all-time/",
    ]

    def parse(self, response):
        for movie in response.css("p.apple-news-link-wrap.movie"):
            # Title
            raw_title = movie.css("span.details a.title::text").get()
            if not raw_title:
                continue
            title = raw_title.strip()

            # Score
            raw_score = movie.css("span.score strong::text").get()
            score = raw_score.replace("%", "").strip() if raw_score else None

            item = RottenItem()
            item["Title"] = title
            item["rottenRating"] = score
            yield item


    
    
