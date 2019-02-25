from scrapy import Request
from scrapytest.tests import Match, Equal, Type, MoreThan, Required

from example.items import PostItem, CommentItem
from example.spiders import HackernewsSpider
from scrapytest.spec import ItemSpec, StatsSpec

# You can define any scrapy settings here
LOG_LEVEL = 'INFO'


class TestPost(ItemSpec):
    # defining item that is being covered
    item_cls = PostItem
    # defining field tests
    title_test = Match('.{5,}')
    points_test = Type(int), MoreThan(0)
    author_test = Type(str), Match('.{3}')
    comments_test = Type(list), Required()

    # also supports methods!
    def url_test(self, value: str):
        if not value.startswith('http'):
            return f'Invalid url: {value}'
        return ''


class TestComments(ItemSpec):
    item_cls = CommentItem
    text_test = Type(str), Match('.{1,}')


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
        "https://news.ycombinator.com/item?id=19187417",
    ]

    def start_requests(self):
        for url in self.test_urls:
            yield Request(url, self.parse_submission)


class TestStats(StatsSpec):
    validate = {
        **StatsSpec.validate,
        'item_scraped_count': Equal(len(TestHackernewsSpider.test_urls)),
    }
