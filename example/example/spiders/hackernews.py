# -*- coding: utf-8 -*-
import scrapy
from scrapy import Item, Request

from example.items import PostItemLoader, CommentItemLoader


class HackernewsSpider(scrapy.Spider):
    name = 'hackernews'
    start_urls = ['https://news.ycombinator.com']

    def parse(self, response):
        for id_ in response.css('.athing::attr(id)').extract():
            url = f'https://news.ycombinator.com/item?id={id_}'
            yield Request(url, self.parse_submission)

    def parse_submission(self, response):
        loader = PostItemLoader(response=response)
        loader.add_css('title', '.title a::text')
        loader.add_css('url', '.title a::attr(href)')
        loader.add_css('author', '.fatitem .hnuser::text')
        loader.add_css('points', '.fatitem .score::text', re='\d+')
        for comment in response.css('.comtr'):
            com_loader = CommentItemLoader(selector=comment)
            com_loader.add_css('text', '.comment ::text')
            loader.add_value('comments', com_loader.load_item())
            break
        yield loader.load_item()
