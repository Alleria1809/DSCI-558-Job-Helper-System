# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LinkedinItem(scrapy.Item):
    job_title = scrapy.Field()
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    job_location = scrapy.Field()
    job_category = scrapy.Field()
    work_type = scrapy.Field()
    job_description = scrapy.Field()

class CompanyurlItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()

class CompanyItem(scrapy.Item):
    name = scrapy.Field()
    description = scrapy.Field()
    type = scrapy.Field()
    industry = scrapy.Field()
    size = scrapy.Field()
    website = scrapy.Field()
    location = scrapy.Field()