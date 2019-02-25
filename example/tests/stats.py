from scrapytest.tests import Equal
from scrapytest.spec import StatsSpec
from tests.spiders import *


class TestStats(StatsSpec):
    spider_cls = TestHackernewsSpider
    validate = {
        **StatsSpec.validate,
        'item_scraped_count': Equal(len(spider_cls.test_urls)),
    }


class TestStats2(StatsSpec):
    spider_cls = TestHackernewsSpider2
    validate = {
        **StatsSpec.validate,
        'item_scraped_count': Equal(len(spider_cls.test_urls)),
    }
