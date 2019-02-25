from scrapy import Request

from example.spiders import HackernewsSpider


class TestHackernewsSpider(HackernewsSpider):
    name = 'test1'
    test_urls = [
        "https://news.ycombinator.com/item?id=19187417",
    ]

    def start_requests(self):
        for url in self.test_urls:
            yield Request(url, self.parse_submission)


class TestHackernewsSpider2(HackernewsSpider):
    name = 'test2'
    test_urls = [
        "https://news.ycombinator.com/item?id=19187410",
    ]

    def start_requests(self):
        for url in self.test_urls:
            yield Request(url, self.parse_submission)
