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
   `validate` attribute with <stat name re pattern>: Test functions
    see StatsSpec.validate
    e.g.
    validate = {
        'some_stat/number/[0-5]': Match('success'),
    }
    `required` attribute contains a list of <stat name re patterns> that
    are required in stat output.
    """
    spider_cls: List = NotImplemented
    validate = {
        'log_count/ERROR$': LessThan(1),
        'item_scraped_count': MoreThan(0),
        'finish_reason': Match('finished'),
    }
    required = []

    def __init__(self):
        self._required_re = {k: re.compile(k) for k in self.required}
        self._validate_re = {k: re.compile(k) for k in self.validate}
        for key, funcs in self.validate.items():
            if not isinstance(funcs, (list, tuple)):
                funcs = [funcs]
            self.validate[key] = Compose(*funcs)
        if not isinstance(self.spider_cls, (list, tuple)):
            self.spider_cls = [self.spider_cls]
        if not isinstance(self.spider_cls, list):
            self.spider_cls = list(self.spider_cls)

    def validate_stats(self, stats: dict) -> List[str]:
        all_messages = []
        for pattern, validation_func in self.validate.items():
            pattern = self._validate_re[pattern]
            for stat, value in stats.items():
                if not pattern.match(stat):
                    continue
                msgs = validation_func(value)
                if msgs:
                    all_messages.extend([f'{stat}: {msg}' for msg in msgs])
        for pattern in self.required:
            compiled = self._required_re[pattern]
            for stat in stats.keys():
                if compiled.match(stat):
                    break
            else:
                all_messages.append(f'{pattern}: missing')

        return all_messages
