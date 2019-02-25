from typing import List, Union

from scrapy import Item
from scrapy.settings import Settings

from scrapytest.spec import ItemSpec, StatsSpec
from scrapytest.utils import get_test_settings


class Validator:
    """
    Main test class that performs validation for specified tests
    """
    def __init__(self, specs: List[Union[ItemSpec, StatsSpec]], settings: Settings):
        self.item_specs = {spec.item_cls: spec for spec in specs if isinstance(spec, ItemSpec)}
        self.stat_specs = {spec.spider_cls: spec for spec in specs if isinstance(spec, StatsSpec)}
        self.settings = settings
        self.skip_items_without_spec = settings.getbool('SKIP_ITEMS_WITHOUT_SPEC')
        self.skip_stats_without_spec = settings.getbool('SKIP_STATS_WITHOUT_SPEC')

    @classmethod
    def from_settings(cls):
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
            stat_spec = self.stat_specs[spider_cls]
        except KeyError as e:
            if self.skip_stats_without_spec:
                return messages
            else:
                return [f'Missing specification for {spider_cls}']
        for msg in stat_spec.validate_stats(stats):
            messages.append(f'{obj_name(stat_spec)}: {msg}')
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
            # deal with nested item
            if isinstance(value, Item):
                messages.extend(self.validate_item(value))
                continue
            # deal with list of nested items
            if isinstance(value, list):
                for v in value:
                    if isinstance(v, Item):
                        msgs = self.validate_item(v)
                        messages.extend(msgs)
            if key not in spec.tests:
                continue
            for msg in spec.tests[key](value):
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
