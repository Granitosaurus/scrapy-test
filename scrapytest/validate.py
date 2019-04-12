from collections import Counter, defaultdict
from typing import List, Union, Dict, Type

from scrapy import Item
from scrapy.settings import Settings

from scrapytest.spec import ItemSpec, StatsSpec
from scrapytest.utils import get_test_settings, join_counter_dicts, is_empty


# TODO add limit to printing length

class Validator:
    """
    Main test class that performs validation for specified tests
    """

    _count_key = '_self'  # used for counting coverage

    def __init__(self, specs: List[Union[ItemSpec, StatsSpec]], settings: Settings):
        self.item_specs = {}
        self.stat_specs = defaultdict(list)
        for spec in specs:
            if isinstance(spec, StatsSpec):
                for spider_cls in spec.spider_cls:
                    self.stat_specs[spider_cls].append(spec)
            if isinstance(spec, ItemSpec):
                self.item_specs[spec.item_cls] = spec
        self.settings = settings
        self.skip_items_without_spec = settings.getbool('SKIP_ITEMS_WITHOUT_SPEC')
        self.skip_stats_without_spec = settings.getbool('SKIP_STATS_WITHOUT_SPEC')
        self.empty_is_missing = settings.getbool('EMPTY_IS_MISSING')

    @classmethod
    def from_settings(cls, settings=None):
        if not settings:
            settings = get_test_settings()
        specs = []
        for key, value in settings.items():
            if value in [ItemSpec, StatsSpec]:
                continue
            if isinstance(value, type) and issubclass(value, (ItemSpec, StatsSpec)):
                specs.append(value())
        return cls(specs=specs, settings=settings)

    def validate_items(self, items):
        for item in items:
            for msg in self.validate_item(item):
                yield msg

    def validate_stats(self, spider_cls, stats):
        messages = []
        try:
            stat_specs = self.stat_specs[spider_cls]
        except KeyError as e:
            if self.skip_stats_without_spec:
                return messages
            else:
                return [f'Missing specification for {spider_cls}']
        for stat_spec in stat_specs:
            for msg in stat_spec.validate_stats(stats):
                messages.append(f'{obj_name(stat_spec)}: {msg}')
        return messages

    def _field_is_missing(self, value):
        if not self.empty_is_missing:
            return False
        return is_empty(value)

    def count_fields(self, items: List[Item]) -> Dict[Type, Counter]:
        """
        Counts all field in list of items
        """
        all_counter = defaultdict(Counter)

        def _count_item(item):
            # check for nested items
            counter = defaultdict(Counter)
            for value in item.values():
                # deal with nested item
                if isinstance(value, Item):
                    counter = join_counter_dicts(counter, _count_item(value))
                    continue
                # deal with list of nested items
                if isinstance(value, list):
                    for v in value:
                        if isinstance(v, Item):
                            counter = join_counter_dicts(counter, _count_item(v))
            counter[type(item)][self._count_key] += 1
            for key in type(item).fields.keys():
                if key in item and not self._field_is_missing(item[key]):
                    counter[type(item)][key] += 1
                else:
                    counter[type(item)][key] = 0
            return counter

        for item in items:
            for item_cls, count in _count_item(item).items():
                all_counter[item_cls] += count
                # also preserve 0 counts
                for k, v in count.items():
                    if v == 0 and k not in all_counter[item_cls]:
                        all_counter[item_cls][k] = 0
        return all_counter

    def validate_coverage(self, items) -> List[str]:
        messages = []
        for item_cls, counter in self.count_fields(items).items():
            try:
                spec = self.item_specs[item_cls]
            except KeyError as e:
                if self.skip_items_without_spec:
                    continue
                else:
                    messages.append(f'Missing specification for {item_cls}')
                    continue
            total_items = counter[self._count_key]
            counter.pop(self._count_key)
            for field, count in counter.most_common():
                expected = spec.coverage.get(field, spec.default_cov)
                perc = count * 100 / total_items
                if perc < expected:
                    messages.append(f'insufficient coverage: {item_cls.__name__}.{field}: '
                                    f'{perc:.2f}%/{expected}% [{count}/{total_items}]')
        return messages

    def validate_item(self, item: Item) -> List:
        """
        Validate item.
        :param item: Srapy.Item object
        :return: list of messages if any failures are encountered
        """
        messages = []
        try:
            spec = self.item_specs[type(item)]
        except KeyError as e:
            if self.skip_items_without_spec:
                return messages
            else:
                return [f'Missing specification for {type(item)}']
        for key, value in item.items():
            if self._field_is_missing(value):
                continue
            # deal with nested item
            if isinstance(value, Item):
                messages.extend(self.validate_item(value))
                continue
            # deal with list of nested items
            if isinstance(value, list):
                for v in value:
                    if isinstance(v, Item):
                        messages.extend(self.validate_item(v))
            test_func = spec.tests.get(key, spec.default_test)
            for msg in test_func(value):
                if not msg:
                    continue
                messages.append(f'{obj_name(item)}.{key}: {msg}')
        return messages


def obj_name(obj):
    try:
        # function
        return obj.__name__
    except:
        # object
        return type(obj).__name__
