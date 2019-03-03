import os
from collections import defaultdict, Counter
from importlib import import_module
from typing import List, Type

from scrapy import Spider
from scrapy.settings import Settings
from scrapy.utils.conf import get_config, init_env
from scrapytest import default_settings
from scrapy.utils.project import ENVVAR


def join_counter_dicts(*items):
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


def get_spiders_from_settings() -> List[Type[Spider]]:
    """Get spider classes from settings"""
    settings = get_test_settings()
    spiders = []
    for key, value in settings.items():
        if isinstance(value, type) and issubclass(value, Spider):
            spiders.append(value)
    return spiders


def get_test_module():
    """get test module name that is contained in scrapy.cfg"""
    config = get_config()
    return config.get('settings', 'test')


def get_test_settings() -> Settings:
    """get test module contents as Settings object"""
    if ENVVAR not in os.environ:
        project = os.environ.get('SCRAPY_PROJECT', 'default')
        init_env(project)
    settings = Settings()
    settings.setmodule(default_settings, priority='default')
    settings_module = import_module(get_test_module())
    for key in dir(settings_module):
        value = getattr(settings_module, key)
        if (isinstance(value, type) and key.lower().startswith('test')) or key.isupper():
            settings.set(key, value, priority='project')
    return settings


def obj_name(obj):
    try:
        # function
        return obj.__name__
    except:
        # object
        return type(obj).__name__
