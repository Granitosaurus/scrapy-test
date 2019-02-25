from scrapytest.tests import Match, Type, MoreThan, Required

from example.items import PostItem, CommentItem
from scrapytest.spec import ItemSpec


class TestPost(ItemSpec):
    # defining item that is being covered
    item_cls = PostItem
    # defining field tests
    title_test = Match('.{5,}')
    points_test = Type(int), MoreThan(0)
    author_test = Type(str), Match('.{3}')
    comments_test = Type(list), Required()

    # also supports methods!
    def url_test(selfself, value: str):
        if not value.startswith('http'):
            return f'Invalid url: {value}'
        return ''


class TestComments(ItemSpec):
    item_cls = CommentItem
    text_test = Type(str), Match('.{1,}')
