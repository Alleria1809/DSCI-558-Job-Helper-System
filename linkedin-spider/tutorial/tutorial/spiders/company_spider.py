import scrapy
import jsonlines
from ..items import CompanyItem

class QuotesSpider(scrapy.Spider):
    name = "company_spider"
    custom_settings = {
        'ITEM_PIPELINES': {
            'tutorial.pipelines.CompanyPipeline': 500,
        }
    }
    def start_requests(self):
        start_urls = []
        with jsonlines.open('../jsonfile/company_url_1_2.jsonl', "r") as f:
            for line in f:
                start_urls.append(line['url'])

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        companyItem = CompanyItem()
        sel = scrapy.Selector(response)
        companyItem['name'] = sel.xpath('//div[@class="top-card-layout__entity-info-container flex flex-wrap papabear:flex-nowrap"]//h1/text()').get()
        companyItem['description'] = sel.xpath('//div[@class="core-section-container__content break-words"]/p/text()').get()
        companyItem['website'] = sel.xpath('//div[@data-test-id="about-us__website"]/dd/a/text()').get()
        companyItem['industry'] = sel.xpath('//div[@data-test-id="about-us__industries"]/dd/text()').get()
        companyItem['size'] = sel.xpath('//div[@data-test-id="about-us__size"]/dd/text()').get()
        companyItem['location'] = sel.xpath('//div[@data-test-id="about-us__headquarters"]/dd/text()').get()
        companyItem['type'] = sel.xpath('//div[@data-test-id="about-us__organizationType"]/dd/text()').get()
        yield companyItem
