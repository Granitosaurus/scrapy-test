from scrapy import Spider

from scrapytest.spec import ItemSpec, StatsSpec
from scrapytest.tests import LessThan

lambda_test = lambda v: v


def test_ItemSpec():
    item_spec = ItemSpec()
    assert list(item_spec.tests) == []
    assert list(item_spec.coverage) == []
    assert item_spec.default_test
    assert item_spec.default_cov

    class MyItemSpec(ItemSpec):
        lambda_test = lambda_test,  # comma important here without it it's a method

        def method_test(self, value):
            return [value]

    assert 'lambda' in MyItemSpec().tests
    assert MyItemSpec().tests['lambda']('foo') == ['foo']
    assert MyItemSpec().tests['method']('foo') == ['foo']

    # test coverage
    class MyItemSpec(ItemSpec):
        foo_cov = 100

    assert MyItemSpec().coverage['foo'] == 100


def test_StatsSpec():
    stats_spec = StatsSpec()
    assert stats_spec._validate_re
    assert isinstance(stats_spec.spider_cls, list)

    # test ensuring spider_cls is list
    class MySpec(StatsSpec):
        spider_cls = Spider

    assert MySpec().spider_cls == [Spider]

    # test ensuring spider_cls is list
    class MySpec(StatsSpec):
        spider_cls = Spider, Spider

    assert MySpec().spider_cls == [Spider, Spider]

    # validate default configuration
    stats = {
        'log_count/ERROR': 100,
        'item_scraped_count': 0,
        'finish_reason': 'test',
    }
    expected = [
        'log_count/ERROR: 100 !< 1',
        'item_scraped_count: 0 !> 1',
        'finish_reason: "test" does not match pettern "finished"',
    ]
    assert MySpec().validate_stats(stats) == expected

    class MySpec(StatsSpec):
        spider_cls = Spider
        validate = {
            'error/code/40[1-5]$': LessThan(1),
        }

    stats = {
        'error/code/402': 5,
        'error/code/409': 5,
    }
    assert MySpec().validate_stats(stats) == ['error/code/402: 5 !< 1']
