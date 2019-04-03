from scrapy import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Compose, Identity, Join


class CommentItem(Item):
    text = Field()


class PostItem(Item):
    title = Field()
    url = Field()
    author = Field()
    points = Field()
    comments = Field()


class PostItemLoader(ItemLoader):
    default_item_class = PostItem
    default_output_processor = TakeFirst()
    points_out = Compose(TakeFirst(), lambda v: int(v) if v else v)
    comments_out = Identity()


class CommentItemLoader(ItemLoader):
    default_item_class = CommentItem
    default_output_processor = Compose(Join(), lambda v: v.strip())
