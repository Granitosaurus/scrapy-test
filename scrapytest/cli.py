import json
from collections import Counter
from time import time

import click
from scrapy import Item
from scrapy.utils.project import get_project_settings

from scrapytest.notifiers import SlackNotifier
from scrapytest.utils import get_spiders_from_settings, get_test_settings, collapse_buffer, get_test_config

from scrapytest.validate import Validator
from scrapytest.runner import run_spiders


def serialize_items(dct):
    if isinstance(dct, Item):
        return dict(dct)
    return dct


def get_spider_cls(name):
    for spider in get_spiders_from_settings():
        if spider.name == name:
            return spider


EXIT_CALLBACKS = {
    0: [],
    1: [],
    'all': [],
}


def exit_msg(code, msg):
    click.echo(msg, err=True)
    callbacks = EXIT_CALLBACKS.get(code, [])
    callbacks += EXIT_CALLBACKS['all']
    for cb in callbacks:
        if isinstance(cb, (tuple, list)) and len(cb) == 2:
            cb, kwargs = cb
        else:
            kwargs = {}
        cb(code, msg, **kwargs)
    exit(code)


def notify_slack(code, msg, config, context=None):
    click.echo(f"sending slack msg to {config['slack_channel']}")
    SlackNotifier.from_config(config).notify(code, msg, context)


NOTIFIERS = {
    'slack': notify_slack,
}


@click.command()
@click.argument('spider-name', required=False)
@click.option('--cache', is_flag=True, help='enable HTTPCACHE_ENABLED setting for this run')
@click.option('--list', 'list_spiders', is_flag=True, help='list spiders with tests')
@click.option('--save', help='save spider results to a file', type=click.File('w'))  # todo support
@click.option('--notify-on-error', help=f'send notification on failure, choice from: {list(NOTIFIERS)}', default='')
@click.option('--notify-on-all', help=f'send notification on failure or success, choice from: {list(NOTIFIERS)}', default='')
@click.option('--notify-on-success', help=f'send notification on success, choice from: {list(NOTIFIERS)}', default='')
@click.option('-c', '--set-config', 'added_config', help='set config value', multiple=True)
@click.option('-s', '--set-setting', 'added_settings', help='set settings value', multiple=True)
def main(spider_name, cache, list_spiders, save, notify_on_error, notify_on_all, notify_on_success, added_config,
         added_settings):  # pragma: no cover
    """run scrapy-test tests and output messages and appropriate exit code (1 for failed, 0 for passed)"""
    # get spiders
    spiders = get_spiders_from_settings()
    if not spiders:
        exit_msg(1, 'ERROR: no spiders found')
    if list_spiders:
        for spider in spiders:
            print(f'{spider.name} @ {spider}')
        exit(0)
    if spider_name:
        spider = get_spider_cls(spider_name)
        if not spider:
            exit_msg(1, f'ERROR: spider {spider_name} not found')
        else:
            spiders = [spider]
    spider_names = [s.__name__ for s in spiders]

    # setup notifiers
    added_config = {k.split('=', 1)[0]: k.split('=', 1)[1] for k in added_config}
    config = {**get_test_config(), **added_config}
    to_notify = {
        0: [n.strip() for n in notify_on_success.split(',') if n.strip()],
        1: [n.strip() for n in notify_on_error.split(',') if n.strip()],
        'all': [n.strip() for n in notify_on_all.split(',') if n.strip()],
    }
    for code, notifiers in to_notify.items():
        for notifier in notifiers:
            kwargs = dict(config=config, context=', '.join(spider_names))
            EXIT_CALLBACKS[code].append((NOTIFIERS[notifier], kwargs))

    # run tests
    start = time()
    messages = []

    added_settings = {k.split('=', 1)[0]: k.split('=', 1)[1] for k in added_settings}
    settings = get_project_settings()
    test_settings = get_test_settings(config)
    settings.update(test_settings, priority=40)
    settings.update(added_settings, priority=50)
    if cache:
        settings['HTTPCACHE_ENABLED'] = True
    results, stats = run_spiders(spiders, settings=settings)
    failures = Counter()
    for spider in spiders:
        buffer, failed = validate_spider(spider, results[spider.name], stats[spider.name])
        failures.update(failed)
        messages.extend(buffer)
    messages = collapse_buffer(messages)

    if save:
        save.write(json.dumps(results, indent=2, default=serialize_items))
        save.close()
    exit_code = 0
    if any(failures.values()):
        exit_code = 1
    end = time()
    messages = [f"{f' elapsed {end - start:.2f} seconds ':=^80}"] + messages
    exit_msg(exit_code, '\n'.join(messages))


def validate_spider(spider_cls, results, stats):  # pragma: no cover
    buffer = []

    def echo(text):
        buffer.append(text)

    validator = Validator.from_settings()

    failed_count = 0
    for msg in validator.validate_items(results):
        echo(msg)
        failed_count += 1

    failed_stats_count = 0
    for msg in validator.validate_stats(spider_cls, stats):
        echo(msg)
        failed_stats_count += 1

    failed_coverage_count = 0
    for msg in validator.validate_coverage(results):
        echo(msg)
        failed_coverage_count += 1

    # if failed_count or failed_stats_count or failed_coverage_count:
    if failed_count:
        echo(f"{f' {spider_cls.__name__} failed {failed_count} field tests ':=^80}")
    if failed_stats_count:
        echo(f"{f' {spider_cls.__name__} failed {failed_stats_count} stat tests ':=^80}")
    if failed_coverage_count:
        echo(f"{f' {spider_cls.__name__} failed {failed_coverage_count} field coverage tests':=^80} ")
    if not any([failed_coverage_count, failed_stats_count, failed_count]):
        echo(f"{f' {spider_cls.__name__} all tests have passed!':=^80} ")
    return buffer, {'item': failed_count, 'stat': failed_stats_count, 'coverage': failed_coverage_count}
