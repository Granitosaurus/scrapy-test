from scrapy import Request

from example.spiders import HackernewsSpider

"""
Test spiders here are extending normal spiders just with controlled and limited
startup.
In this case we override HackernewsSpider to skip discovering articles and instead
go to articles we define explicitly.
"""


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
