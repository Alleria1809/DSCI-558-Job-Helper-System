import scrapy
from ..items import LinkedinItem

class QuotesSpider(scrapy.Spider):
    name = "lnkedin_spider"
    custom_settings = {
        'ITEM_PIPELINES': {
            'tutorial.pipelines.LinkedinPipeline': 300,
        }
    }
    def start_requests(self):
        start_urls = []
        categories = ['Data Scientist', 'HR', 'Lawyer', 'Artist', 'Web Designer', 'Mechanical Engineer', 'Salesman', 'Civil Engineer',
                  'Software Developer', 'Business Analyst', 'Automation Tester', 'Electrical Engineer', 'Operations Manager',
                  'Network Security Engineer', 'Product Manager']
        for c in categories[1:]:
            category = c.lower().replace(" ", "%20")
            with open(f'../txtfile_category/links_{category}.txt', "r") as f:
                for line in f:
                    start_urls.append(line)
            for url in start_urls:
                yield scrapy.Request(url=url, callback=self.parse, meta={'category': c})

    def parse(self, response):
        jobItem = LinkedinItem()
        sel = scrapy.Selector(response)
        #job_category = sel.xpath("//input[contains(@aria-label, 'Search job titles or companies')]/@value").get()
        #jobItem["job_category"] = job_category
        print(response.meta['category'])
        jobItem["job_category"] = response.meta['category']
        job_title = sel.xpath('//h1[contains(@class, "top-card-layout__title")]/text()').get()
        if job_title is not None:
            jobItem["job_title"] = " ".join(job_title.split())
        else:
            jobItem["job_title"] = None

        company_name = sel.xpath('//span[@class="topcard__flavor"]//text()').getall()
        if company_name is not None:
            jobItem["company_name"] = " ".join((" ".join(company_name)).split())
        else:
            jobItem["company_name"] = None

        jobItem["company_url"] = sel.xpath('//span[@class="topcard__flavor"]/a/@href').get()

        company_location = sel.xpath('//span[contains(@class, "topcard__flavor topcard__flavor--bullet")]/text()').get()
        if company_location is not None:
            jobItem["job_location"] = " ".join(company_location.split())
        else:
            jobItem["job_location"] = None

        '''work_method = sel.xpath('//span[contains(@class, "jobs-unified-top-card__workplace-type")]/text()').get()
        if work_method is not None:
            jobItem["work_method"] = " ".join(work_method.split())
        else:
            jobItem["work_method"] = None
        print("work_method", jobItem['work_method'])'''

        work_type = sel.xpath('//li[h3[contains(text(), "Employment type")]]/span/text()').get()
        if work_type is not None:
            jobItem["work_type"] = " ".join(work_type.split())
        else:
            jobItem["work_type"] = None

        job_des = sel.xpath('//div[contains(@class, "show-more-less-html__markup")]//text()').getall()
        jobItem['job_description'] = job_des

        yield jobItem