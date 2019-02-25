import re
from scrapytest.tests import LessThan, MoreThan, Match, Compose


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
    tests = {}

    def __init__(self):
        for k in dir(self):
            if not k.endswith('_test'):
                continue
            funcs = getattr(self, k)
            if not isinstance(funcs, (list, tuple)):
                funcs = [funcs]
            self.tests[k.split('_test')[0]] = Compose(*funcs)


class StatsSpec:
    """
    Scrapy stats specification.
    Should contain `validate` attribute with <stat name re pattern>: Test functions
    see StatsSpec.validate
    """
    spider_cls = NotImplemented
    validate = {
        'log_count/ERROR$': LessThan(1),
        'item_scraped_count': MoreThan(1),
        'finish_reason': Match('finished'),
    }

    def __init__(self):
        self._validate_re = {k: re.compile(k) for k in self.validate}

    def validate_stats(self, stats):
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

