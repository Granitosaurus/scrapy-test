import re

from scrapytest.utils import is_empty

try:
    from typeguard import check_type

    HAS_TYPEGUARD = True
except ImportError:
    HAS_TYPEGUARD = False

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


class Map:
    """Map set of tests to every value"""

    def __init__(self, *functions):
        self.functions = functions

    def __call__(self, values):
        all_messages = []
        for func in self.functions:
            for value in values:
                try:
                    messages = func(value)
                    all_messages.extend(messages if isinstance(messages, list) else [messages])
                except TypeError as e:
                    all_messages.append(f'{type(e).__name__}:{e} got "{type(value)}": {value}')
                except Exception as e:
                    all_messages.append(f'{type(e).__name__}:{e} "{value}"')
        return [msg for msg in all_messages if msg]

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
            except TypeError as e:
                all_messages.append(f'{type(e).__name__}:{e} got "{type(value)}": {value}')
            except Exception as e:
                all_messages.append(f'{type(e).__name__}:{e}')
        return [msg for msg in all_messages if msg]

    def __str__(self):
        full = []
        for fun in self.functions:
            full.append(str(fun))
        return ','.join(full)


class Match:
    """Regex pattern match tester"""

    def __init__(self, pattern, flags=0):
        self.pattern = re.compile(pattern, flags=flags)

    def __call__(self, value):
        if not self.pattern.match(value):
            return f'"{value}" does not match pattern "{self.pattern.pattern}"'
        return ''


class Search:
    """Regex pattern search tester"""

    def __init__(self, pattern, flags=0):
        self.pattern = re.compile(pattern, flags=flags)

    def __call__(self, value):
        if not self.pattern.search(value):
            return f'"{value}" does contain pattern "{self.pattern.pattern}"'
        return ''


class _Compare:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f'{type(self).__name__}({self.value})'


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
        return f'{type(value).__name__}:{value} != {type(self.value).__name__}:{self.value}'


class MoreThan(_Compare):
    """Test whether value is more than some other value"""

    def __call__(self, value):
        if value > self.value:
            return ''
        return f'{value} !> {self.value}'


class Required:
    """Test whether value exists"""

    def __call__(self, value):
        if is_empty(value):
            return f'is empty value: "{value}" of type {type(value).__name__}'
        return ''


class Pass:
    def __call__(self, *args, **kwargs):
        return ''


class Type:
    """Check whether value matches a type"""

    def __init__(self, type):
        if not HAS_TYPEGUARD:
            raise ImportError('typeguard is required for type matching: pip install typeguard')
        self.type = type

    def __call__(self, value):
        try:
            check_type('', value, self.type)
        except TypeError as e:
            return e.args[0]
        return ''

    def __eq__(self, other):
        return isinstance(other, Type) and self.type == other.type
