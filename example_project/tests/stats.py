from scrapytest.tests import Equal, Required
from scrapytest.spec import StatsSpec
from tests.spiders import *

"""
Stats tests are defined here for testing stats of finished crawl
"""


class TestStats(StatsSpec):
    spider_cls = TestHackernewsSpider
    validate = {
        **StatsSpec.validate,  # include defaults
        # should be as many results as there are urls scheduled
        'item_scraped_count': Equal(len(TestHackernewsSpider.test_urls)),
    }


class TestStats2(StatsSpec):
    # test just defaults for this one
    spider_cls = TestHackernewsSpider2
    validate = {
        'item_scraped_count': (Equal("I'm here!"), Equal('meow')),
        # 'some_missing_stat': Equal("I'm here!"),
    }
    required = [
        'some_missing_stat',
    ]
