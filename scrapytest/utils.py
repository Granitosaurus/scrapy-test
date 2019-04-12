import os
from collections import defaultdict, Counter
from importlib import import_module
from typing import List, Type

from scrapy import Spider
from scrapy.settings import Settings
from scrapy.utils.conf import get_config, init_env
from scrapytest import default_settings
from scrapy.utils.project import ENVVAR

from scrapytest.exceptions import ConfigError


def collapse_buffer(buffer, format='{msg} [x{count}]'):
    """
    collapse repeating messages and add count:

    >>> collapse_buffer(['foo', 'foo'])
    ['foo [2]']
    """
    counter = Counter()
    for msg in buffer:
        counter[msg] += 1
    collapsed = []
    for msg, count in counter.items():
        if count == 1:
            collapsed.append(msg)
        else:
            collapsed.append(format.format(msg=msg, count=count))
    return collapsed


def is_empty(value) -> bool:
    try:
        iter(value)  # non-iterable values can't be empty, e.g. 0, False
    except TypeError:
        return False
    return not bool(value)


def join_counter_dicts(*items) -> defaultdict:
    """
    Combine dictionaries of counters, i.e.:
    {'foo': Counter('key': 1)}
    +
    {'foo': Counter('key': 2)}
    =
    {'foo': Counter('key': 3)}

    """
    merged = defaultdict(Counter)
    for item in items:
        for key, count in item.items():
            # ensure that zero counts are preserved as every counter update eliminates them
            zeroes = {k: v for k, v in merged[key].items() if v == 0}
            merged[key] += count
            # lazy update zero keys
            for k, v in zeroes.items():
                if v == 0 and k not in merged[key]:
                    merged[key][k] = 0
            for k, v in count.items():
                if v == 0 and k not in merged[key]:
                    merged[key][k] = 0
    return merged


def get_spiders_from_settings(settings=None) -> List[Type[Spider]]:  # pragma: no cover
    """Get spider classes from settings"""
    if not settings:
        settings = get_test_settings()
    spiders = []
    for key, value in settings.items():
        if isinstance(value, type) and issubclass(value, Spider):
            spiders.append(value)
    return spiders


def get_test_config(config=None):
    """get [test] config section of scrapy.cfg"""
    if not config:
        config = get_config()
    try:
        return config['test']
    except KeyError:
        raise ConfigError('scrapytest configuration is missing in scrapy.cfg, required "[test]" section')


def get_test_settings(config=None) -> Settings:  # pragma: no cover
    """get test module contents as Settings object from scrapy-test config section"""
    if not config:
        config = get_test_config()
    if ENVVAR not in os.environ:
        project = os.environ.get('SCRAPY_PROJECT', 'default')
        init_env(project)
    settings = Settings()
    settings.setmodule(default_settings, priority='default')
    settings_module = import_module(config['root'])
    for key in dir(settings_module):
        value = getattr(settings_module, key)
        if (isinstance(value, type) and key.lower().startswith('test')) or key.isupper():
            settings.set(key, value, priority='project')
    return settings


def obj_name(obj) -> str:
    try:
        # function
        return obj.__name__
    except:
        # object
        return type(obj).__name__
