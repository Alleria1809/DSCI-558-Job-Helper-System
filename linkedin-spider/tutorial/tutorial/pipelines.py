# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json

class LinkedinPipeline:

    def open_spider(self, spider):
        self.file = open('../jsonfile_category/job_positions1.jsonl', 'ab')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
        self.file.write(line.encode("utf-8"))
        return item

class CompanyurlPipeline:

    def open_spider(self, spider):
        self.file = open('../jsonfile/company_url.jsonl', 'wb')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
        self.file.write(line.encode("utf-8"))
        return item

class CompanyPipeline:

    def open_spider(self, spider):
        self.file = open('../jsonfile/linkedin_company.jsonl', 'wb')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
        self.file.write(line.encode("utf-8"))
        return item