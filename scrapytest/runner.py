from collections import defaultdict
from typing import Tuple

from scrapy import signals
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.settings import default_settings
from scrapy.utils.log import configure_logging, log_scrapy_info
from scrapy.utils.project import get_project_settings

from scrapy.signalmanager import dispatcher
from twisted.internet import reactor

"""
Running scrapy crawlers in python.
see https://doc.scrapy.org/en/latest/topics/practices.html#run-scrapy-from-a-script
"""


# TODO spider_kwargs should probably be per spider?
def run_spiders(spiders, settings=None, **spider_kwargs) -> Tuple[dict, dict]:
    """
    Crawl multiple spiders and return their results and stats:
    e.g.
    {'spider1': [], 'spider2': []}, {'spider1': {}, 'spider2': {}}
    """
    results = defaultdict(list)
    stats = defaultdict(dict)

    def crawler_results(signal, sender, item, response, spider):
        results[spider.name].append(item)

    def crawler_close(signal, sender, spider, reason):
        stats[spider.name].update(spider.crawler.stats.get_stats())

    dispatcher.connect(crawler_results, signal=signals.item_passed)
    dispatcher.connect(crawler_close, signal=signals.spider_closed)

    all_settings = get_project_settings()
    # update settings
    all_settings.setmodule(default_settings)
    all_settings.setdict(settings, priority='cmdline')

    runner = CrawlerProcess(all_settings)
    configure_logging(all_settings, True)
    log_scrapy_info(all_settings)
    d = runner.crawl(spiders[0], **spider_kwargs)
    if len(spiders) > 1:
        for spider in spiders[1:]:
            d.addBoth(lambda _: runner.crawl(spider, **spider_kwargs))
    d.addBoth(lambda _: reactor.stop())
    reactor.run()  # the script will block here until the crawling is finished
    return results, stats
