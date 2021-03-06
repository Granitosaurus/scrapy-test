from collections import Counter

from scrapytest.utils import join_counter_dicts, is_empty, obj_name, collapse_buffer


def test_collapse_buffer():
    messages = [
        'one',
        'two',
        'two',
        'three',
        'two'
    ]
    expected = [
        'one', 'two [x3]', 'three'
    ]
    assert collapse_buffer(messages) == expected


def test_is_empty():
    assert is_empty('') is True
    assert is_empty(0) is False
    assert is_empty(False) is False
    assert is_empty('foo') is False


def test_obj_name():
    assert obj_name('something') == 'str'
    assert obj_name(str) == 'str'


def test_join_counter_dicts():
    # join two together
    inp = (
        {'key1': Counter({'field1': 5, 'field2': 10})},
        {'key1': Counter({'field1': 1, 'field2': 1})},
    )
    expected = {'key1': Counter({'field1': 6, 'field2': 11})}
    assert dict(join_counter_dicts(*inp)) == expected

    # join more than two together
    inp = (
        {'key1': Counter({'field1': 5, 'field2': 10})},
        {'key1': Counter({'field1': 1, 'field2': 1})},
        {'key1': Counter({'field1': 1, 'field2': 1})},
        {'key1': Counter({'field1': 1, 'field2': 1})},
    )
    expected = {'key1': Counter({'field1': 8, 'field2': 13})}
    assert dict(join_counter_dicts(*inp)) == expected

    # join different schemas
    inp = (
        {'key1': Counter({'field1': 5, 'field2': 10})},
        {'key2': Counter({'field1': 1, 'field2': 1})},
    )
    expected = {
        'key1': Counter({'field1': 5, 'field2': 10}),
        'key2': Counter({'field1': 1, 'field2': 1}),
    }
    assert dict(join_counter_dicts(*inp)) == expected

    # ensure zeroes are preserved
    inp = (
        {'key1': Counter({'field1': 5, 'field2': 10, 'field3': 0})},
        {'key1': Counter({'field1': 1, 'field2': 1})},
    )
    expected = {'key1': Counter({'field1': 6, 'field2': 11, 'field3': 0})}
    assert dict(join_counter_dicts(*inp)) == expected

    # ensure zeroes are preserved
    inp = (
        {'key1': Counter({'field1': 5, 'field2': 10, 'field3': 0})},
        {'key1': Counter({'field1': 1, 'field2': 1, 'field3': 1})},
    )
    expected = {'key1': Counter({'field1': 6, 'field2': 11, 'field3': 1})}
    assert dict(join_counter_dicts(*inp)) == expected

    # everything together
    inp = (
        {'key1': Counter({'field1': 5, 'field2': 10})},
        {'key1': Counter({'field1': 1, 'field2': 1, 'field3': 0})},
        {'key2': Counter({'field1': 5, 'field2': 5})},
    )
    expected = {
        'key1': Counter({'field1': 6, 'field2': 11, 'field3': 0}),
        'key2': Counter({'field1': 5, 'field2': 5}),
    }
    assert dict(join_counter_dicts(*inp)) == expected
