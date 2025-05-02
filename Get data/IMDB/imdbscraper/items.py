import scrapy

class Info(scrapy.Item):
    Title = scrapy.Field()
    imdbRating = scrapy.Field()

