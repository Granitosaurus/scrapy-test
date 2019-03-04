import re
from typing import List

from scrapytest.tests import LessThan, MoreThan, Match, Compose, Pass


class ItemSpec:
    """
    Item specification for tests.
    Usage:

    class MyItemSpec:
        item_cls = MyItem
        # with lambdas
        field_test = lambda value: 'failure' if value < 100 else ''
        # with inbuilt testers
        field2_test = Match('foobar\d+')
        field3_test = Type(int), MoreThan(1), LessThan(5)
    """
    item_cls = NotImplemented
    tests = None
    coverage = None
    default_cov = 0.1
    default_test = Pass()

    def __init__(self):
        self.coverage = {}
        self.tests = {}
        for k in dir(self):
            if k.endswith('_test') and k != 'default_test':
                funcs = getattr(self, k)
                if not isinstance(funcs, (list, tuple)):
                    funcs = [funcs]
                self.tests[k.split('_test')[0]] = Compose(*funcs)
            if k.endswith('_cov') and k != 'default_cov':
                self.coverage[k.split('_cov')[0]] = getattr(self, k)


class StatsSpec:
    """
    Scrapy stats specification.
    Should contain `validate` attribute with <stat name re pattern>: Test functions
    see StatsSpec.validate
    e.g.
    validate = {
        'some_stat/number/[0-5]': Match('success'),
    }
    """
    spider_cls: List = NotImplemented
    validate = {
        'log_count/ERROR$': LessThan(1),
        'item_scraped_count': MoreThan(1),
        'finish_reason': Match('finished'),
    }

    def __init__(self):
        self._validate_re = {k: re.compile(k) for k in self.validate}
        if not isinstance(self.spider_cls, (list, tuple)):
            self.spider_cls = [self.spider_cls]
        if not isinstance(self.spider_cls, list):
            self.spider_cls = list(self.spider_cls)

    def validate_stats(self, stats: dict) -> List[str]:
        all_messages = []
        for key, value in stats.items():
            for k, validation in self._validate_re.items():
                if validation.match(key):
                    validation_func = self.validate[k]
                    break
            else:
                continue
            msg = validation_func(value)
            if msg:
                all_messages.append(f'{key}: {msg}')
        return all_messages
