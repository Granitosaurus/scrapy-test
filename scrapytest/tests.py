import re
from typing import Iterable

"""
These are base testers for scrapy-test framework

tester is a callable that takes value and 
returns a message or list of messages if some errors are encountered

e.g. 
    def some_test(value):
        if value == 'cake':
            return 'no cake :('
        return ''
"""


def to_list(value):
    if isinstance(value, (list, tuple)):
        return list(value)
    return value


class Map:
    def __init__(self, *functions):
        self.functions = functions

    def __call__(self, values):
        all_messages = []
        for func in self.functions:
            for value in values:
                try:
                    messages = func(value)
                    all_messages.extend(messages if isinstance(messages, list) else [messages])
                except Exception as e:
                    all_messages.append(f'{type(e).__name__}:{e}')
        return all_messages

    def __str__(self):
        full = []
        for fun in self.functions:
            full.append(str(fun))
        return ','.join(full)


class Compose:
    """Combine multiple testers"""

    def __init__(self, *functions):
        self.functions = functions

    def __call__(self, value):
        all_messages = []
        for func in self.functions:
            try:
                messages = func(value)
                all_messages.extend(messages if isinstance(messages, list) else [messages])
            except Exception as e:
                all_messages.append(f'{type(e).__name__}:{e}')
        return all_messages

    def __str__(self):
        full = []
        for fun in self.functions:
            full.append(str(fun))
        return ','.join(full)


class Match:
    """Regex pattern match tester"""

    def __init__(self, pattern):
        self.pattern = re.compile(pattern)

    def __call__(self, value):
        if not self.pattern.match(value):
            return f'"{value}" does not match pettern "{self.pattern.pattern}"'
        return ''


class _Compare:
    def __init__(self, value):
        self.value = value


class Len:
    class less_than(_Compare):
        def __call__(self, value):
            if len(value) < self.value:
                return ''
            return f'length {len(value)} when expected <{self.value}'

    class more_than(_Compare):
        def __call__(self, value):
            if len(value) > self.value:
                return ''
            return f'length {len(value)} when expected >{self.value}'

    class equals(_Compare):
        def __call__(self, value):
            if len(value) == self.value:
                return ''
            return f'length {len(value)} when expected ={self.value}'


if __name__ == '__main__':
    print(Len.less_than(5)('hello'))


class LessThan(_Compare):
    """Test whether value is less than some other value"""

    def __call__(self, value):
        if value < self.value:
            return ''
        return f'{value} !< {self.value}'


class Equal(_Compare):
    """Test whether value is equal to some other value"""

    def __call__(self, value):
        if value == self.value:
            return ''
        return f'{value} != {self.value}'


class MoreThan(_Compare):
    """Test whether value is more than some other value"""

    def __call__(self, value):
        if value > self.value:
            return ''
        return f'{value} !> {self.value}'


class Required:
    """Test whether value exists"""

    def __call__(self, value):
        if not value:
            return f'{value} is empty'
        return ''


class Type:
    """Check whether value matches a type"""

    def __init__(self, type):
        self.type = type

    def __call__(self, value):
        if not isinstance(value, self.type):
            return f'{value} is unexpected type {type(value)}, expected {self.type}'
        return ''

    def __eq__(self, other):
        return isinstance(other, Type) and self.type == other.type
