import json

import click
from scrapytest.utils import get_spiders_from_settings, get_test_settings

from scrapytest.validate import Validator
from scrapytest.runner import run_spiders


def get_spider_cls(name):
    for spider in get_spiders_from_settings():
        if spider.name == name:
            return spider


@click.command()
@click.argument('spider-name', required=False)
@click.option('-c', '--cache', is_flag=True, help='enable HTTPCACHE_ENABLED setting for this run')
def main(spider_name, cache):
    """run scrapy-test tests and output messages and appropriate exit code (1 for failed, 0 for passed)"""
    if spider_name:
        spiders = [get_spider_cls(spider_name)]
    else:
        spiders = get_spiders_from_settings()
    messages = []
    settings = get_test_settings()
    if cache:
        settings['HTTPCACHE_ENABLED'] = True
    results, stats = run_spiders(spiders, settings=settings)
    for spider in spiders:
        messages.extend(validate_spider(spider, results[spider.name], stats[spider.name]))
    click.echo(f"{'crawling results':=^80}", err=True)
    for msg in messages:
        click.echo(msg, err=True)
    if len(messages) > len(spiders) * 2:  # means some tests failed to pass
        exit(1)
    else:
        exit(0)


def validate_spider(spider_cls, results, stats):
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
    if failed_count or failed_stats_count:
        echo(f"{f'failed {failed_count} field tests and {failed_stats_count} stat tests':=^80}")
    else:
        echo(f"{f'{spider_cls.__name__} all tests have passed!':=^80}")
    return buffer
