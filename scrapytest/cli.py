import json
from time import time

import click
from scrapy import Item

from scrapytest.utils import get_spiders_from_settings, get_test_settings, collapse_buffer

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


@click.command()
@click.argument('spider-name', required=False)
@click.option('-c', '--cache', is_flag=True, help='enable HTTPCACHE_ENABLED setting for this run')
@click.option('--list', 'list_spiders', is_flag=True, help='list spiders with tests')
@click.option('--save', help='save spider results to a file', type=click.File('w'))  # todo support
def main(spider_name, cache, list_spiders, save):  # pragma: no cover
    """run scrapy-test tests and output messages and appropriate exit code (1 for failed, 0 for passed)"""
    start = time()
    spiders = get_spiders_from_settings()
    if not spiders:
        click.echo('ERROR: no spiders found')
        exit(1)
    if list_spiders:
        for spider in spiders:
            print(f'{spider.name} @ {spider}')
        exit(0)
    if spider_name:
        spider = get_spider_cls(spider_name)
        if not spider:
            click.echo(f'ERROR: spider {spider_name} not found')
            exit(1)
        else:
            spiders = [spider]
    messages = []
    settings = get_test_settings()
    if cache:
        settings['HTTPCACHE_ENABLED'] = True
    results, stats = run_spiders(spiders, settings=settings)
    for spider in spiders:
        messages.extend(validate_spider(spider, results[spider.name], stats[spider.name]))
    for msg in collapse_buffer(messages):
        click.echo(msg, err=True)
    end = time()
    click.echo(f"{f'elapsed {end - start:.2f} seconds':=^80}", err=True)
    if save:
        save.write(json.dumps(results, indent=2, default=serialize_items))
        save.close()
    if len(messages) > len(spiders) * 2:  # means some tests failed to pass
        exit(1)
    else:
        exit(0)


def validate_spider(spider_cls, results, stats):  # pragma: no cover
    buffer = []

    def echo(text):
        buffer.append(text)

    echo(f"{f'{spider_cls.__name__} validating results':=^80}")
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
        echo(f"{f'failed {failed_count} field tests':=^80}")
    if failed_stats_count:
        echo(f"{f'failed {failed_stats_count} stat tests':=^80}")
    if failed_coverage_count:
        echo(f"{f'failed {failed_coverage_count} field coverage tests':=^80}")
    if not any([failed_coverage_count, failed_stats_count, failed_count]):
        echo(f"{f'{spider_cls.__name__} all tests have passed!':=^80}")
    return buffer
