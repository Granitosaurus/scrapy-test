import re
from urllib.parse import urlparse

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


class Only:
    def __init__(self, values):
        self.values = values

    def __call__(self, value):
        bad = [c for c in value if c not in self.values]
        if bad:
            return f'value "{value}" contains disallowed values: {bad}'
        return ''


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


class Url:
    """
    Test url parts with defined regex patterns
    """

    def __init__(self, netloc='', path='', params='', query='', fragment='', is_absolute=True):
        self.path = re.compile(path) if path else None
        self.params = re.compile(params) if params else None
        self.query = re.compile(query) if query else None
        self.fragment = re.compile(fragment) if fragment else None
        self.netloc = re.compile(netloc) if netloc else None
        self.is_absolute = is_absolute

    def __call__(self, value):
        url = urlparse(value)
        if self.is_absolute and not url.netloc:
            return f'not an absolute url: {value}'
        for key in ['netloc', 'path', 'params', 'query', 'fragment']:
            pattern = getattr(self, key)
            value = getattr(url, key)
            if pattern and not pattern.search(value):
                return f'mismatched url.{key}: "{value}" expected: "{pattern.pattern}"'
        return ''


class Any:
    """pass at least one of supplied test function"""

    def __init__(self, *funcs):
        self.funcs = funcs

    def __call__(self, value):
        messages = []
        for func in self.funcs:
            msg = func(value)
            if not msg:
                return []
            messages.append(msg)
        return messages


class Type:
    """Check whether value matches a type"""

    def __init__(self, type):
        if not HAS_TYPEGUARD:
            raise ImportError('typeguard is required for type matching: pip install typeguard')
        self.type = type

    def __call__(self, value):
        try:
            check_type('', value, self.type)
        except TypeError:
            return f'{value} is unexpected type {type(value)}, expected {self.type}'
        return ''

    def __eq__(self, other):
        return isinstance(other, Type) and self.type == other.type
