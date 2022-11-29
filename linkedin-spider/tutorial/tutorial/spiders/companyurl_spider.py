import scrapy
from ..items import CompanyurlItem

class QuotesSpider(scrapy.Spider):
    name = "companyurl_spider"
    custom_settings = {
        'ITEM_PIPELINES': {
            'tutorial.pipelines.CompanyurlPipeline': 400,
        }
    }
    def start_requests(self):
        start_urls = []
        with open('../txtfile/links_company.txt', "r") as f:
            for line in f:
                start_urls.append(line)
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        urlItem = CompanyurlItem()
        sel = scrapy.Selector(response)
        company_name = sel.xpath('//span[@class="topcard__flavor"]//text()').getall()
        if company_name is not None:
            urlItem["name"] = " ".join((" ".join(company_name)).split())
        else:
            urlItem["name"] = None
        company_url = sel.xpath('//span[@class="topcard__flavor"]/a/@href').get()
        urlItem['url'] = company_url
        yield urlItem
